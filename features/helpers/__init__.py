import docker

from .local_registry import LocalRegistry

client = docker.from_env()
