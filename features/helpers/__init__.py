import docker

from .local_registry import LocalRegistry
from .docker_build import DockerBuild
from .lazy_kaniko_run import LazyKanikoRun

client = docker.from_env()

DOCKER_NETWORK = "lazy_kaniko_behave"

def setup_networking():
    networks = client.networks.list(names=[DOCKER_NETWORK])
    if len(networks) == 0:
        return client.networks.create(DOCKER_NETWORK)
    else:
        return networks[0]
