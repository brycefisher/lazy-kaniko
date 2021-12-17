import docker

from .local_registry import LocalRegistry
from .docker_build import DockerBuild

client = docker.from_env()
