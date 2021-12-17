import docker

from .local_registry import LocalRegistry
from .docker_build import DockerBuild
from .lazy_kaniko_run import LazyKanikoRun

client = docker.from_env()


def setup_networking():
    return client.networks.create("lazy_kaniko_behave")
