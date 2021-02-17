from dataclasses import dataclass
from os.path import abspath
from textwrap import indent
import json

import docker

client = docker.from_env()


class Registry:
    """ Resource handle for ephemeral, test-specific docker registry """

    image = 'registry:2.7.1'

    def __init__(self):
        self.name = "registry"
        self._container = client.containers.run(self.image, name=self.name, ports={"5000/tcp": 5000}, detach=True)

    @property
    def address(self):
        return f"{self.name}:5000"

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
        self.execute()

    def __del__(self):
        self._container.remove(force=True)

    def volumes(self):
        return [
            self.build.context_mount(),
        ]

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

    def debug(self):
        header = f"=====[ {self._container.name} ({self.sut_image_tag}) ]====="
        container_inspect = json.dumps(self._container.attrs, indent=4)
        logs = indent(self._container.logs().decode().strip(), " > ")
        footer = "=" * len(header)
        return "\n".join([header, container_inspect, logs, footer])


# THINGS NEEDED TO RUN THIS:
#  - target image name
#  - Dockerfile
#  - build context
#
# THINGS PROVIDED BY THIS IMAGE:
#  - target image tag
#  - output docker image
#  - docker push
