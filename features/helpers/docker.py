from dataclasses import dataclass
from os.path import abspath
from textwrap import indent
from typing import Optional
import csv
import json

from . import LocalRegistry


# TODO - break into separate module
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


# TODO - break into separate module
@dataclass
class LazyKanikoRun:
    """ Execution of System-Under-Test """
    registry: LocalRegistry
    build: DockerBuild
    user: Optional[str] = None
    password: Optional[str] = None
    sut_tag: str = "latest"

    image = "brycefisherfleig/lazy-kaniko"

    def __post_init__(self):
        from . import client
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
    from . import client
    return client.networks.create("lazy_kaniko_behave")
