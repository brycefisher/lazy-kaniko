from dataclasses import dataclass
from os.path import abspath
from textwrap import indent
import csv
import json

from . import client


class Registry:
    """ Resource handle for ephemeral, test-specific docker registry """

    image = 'registry:2.7.1'

    def __init__(self, auth = False, local_port = 5000):
        self.name = "registry"
        self._env = {}
        self._volumes = {}
        self.local_port = local_port

        if auth:
            self._require_auth()

        self._run()

    def _run(self):
        self._container = client.containers.run(self.image,
                                                name=self.name,
                                                environment=self._env,
                                                volumes=self._volumes,
                                                ports={"5000/tcp": self.local_port},
                                                detach=True)

    @property
    def address(self):
        return f"{self.name}:{self.local_port}"

    @property
    def local_address(self):
        return f"localhost:{self.local_port}"

    @property
    def id(self):
        return self._container.id

    def _require_auth(self):
        self._env['REGISTRY_AUTH'] = 'htpasswd'
        self._env['REGISTRY_AUTH_HTPASSWD_REALM'] = 'Registry'
        self._env['REGISTRY_AUTH_HTPASSWD_PATH'] = '/etc/docker/registry/htpasswd'
        self._volumes['/home/bff/programming/lazy-kaniko/helpers/htpasswd'] = {
            'bind': '/etc/docker/registry/htpasswd',
            'mode': 'ro',
        }

    def __del__(self):
        self._container.remove(force=True)


class DockerBuild:
    """
    Test Case comprised of a Dockerfile and build context

     * Build contexts are subdirectories at `features/builds/{build_name}`
     * Dockerfiles exist in `features/builds/{build_name}/Dockerfile`
    """

    def __init__(self, build_name: str):
        self.name = build_name
        self.build_context = f"features/builds/{build_name}/"
        # TODO -- check the build context and a Dockerfile within the build context all exist

    def context_mount(self):
        container_path = "/workspace"
        host_path = abspath(self.build_context)
        return f"{host_path}:{container_path}:ro"

    @property
    def tag(self):
        with open("features/builds/tags.json") as fd:
            builds = json.load(fd)
            return builds[self.name]

@dataclass
class LazyKanikoRun:
    """ Execution of System-Under-Test """
    registry: Registry
    build: DockerBuild
    sut_tag: str = "latest"

    image = "brycefisherfleig/lazy-kaniko"

    def __post_init__(self):
        self.target_image = f"{self.registry.address}/{self.build.name}"
        self._container = client.containers.create(self.sut_image_tag, environment=self.environment, volumes=self.volumes())

    def __del__(self):
        self._container.remove(force=True)

    def volumes(self):
        return [self.build.context_mount()]

    @property
    def sut_image_tag(self):
        return f"{self.image}:{self.sut_tag}"

    @property
    def environment(self):
        return {
            "TARGET_IMAGE": self.target_image,
            "DOCKERFILE": "/workspace/Dockerfile",
            "CONTEXT": "/workspace/",
        }

    def execute(self):
        self._container.start()
        self._result = self._container.wait(timeout=30)

    def logs(self):
        return self._container.logs().decode().strip()

    @property
    def id(self):
        return self._container.id

    def debug(self):
        header = f"=====[ {self._container.name} ({self.sut_image_tag}) ]====="
        logs = indent(self.logs(), " > ")
        footer = "=" * len(header)
        return "\n".join([header, logs, footer])


def setup_networking():
    return client.networks.create("lazy_kaniko_behave")
