from dataclasses import dataclass
from textwrap import indent
from typing import Optional

from . import LocalRegistry, DockerBuild


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
