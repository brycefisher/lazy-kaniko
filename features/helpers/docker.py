from dataclasses import dataclass

import docker

client = docker.from_env()


class Registry:
    """ Resource handle for ephemeral, test-specific docker registry """

    image = 'registry:2.7.1'

    def __init__(self):
        self.name = "registry"
        self._container = client.containers.run(self.image, name=self.name, detach=True)

    @property
    def address(self):
        return f"{self.name}:5000"

    def __del__(self):
        self._container.remove(force=True)


class DockerBuild:
    """
    Test Case comprised of a Dockerfile and build context

     * Dockerfiles exist in `features/builds/Dockerfile-{build_name}`
     * Build contexts are subdirectories at `features/builds/{build_name}`
    """

    def __init__(self, build_name: str):
        self.name = build_name
        self.build_context = f"features/builds/{build_name}/"
        with open(f'features/builds/Dockerfile-{build_name}') as dockerfile:
            self.dockerfile = dockerfile.read()


@dataclass
class LazyKanikoRun:
    """ Execution of System-Under-Test """
    registry: Registry
    build: DockerBuild
    sut_tag: str = "latest"

    image = "brycefisherfleig/lazy-kaniko"

    def __post_init__(self):
        self.target_image = f"{self.registry.address}/{self.build.name}"
        self.execute()

    @property
    def sut_image_tag(self):
        return f"{self.image}:{self.sut_tag}"

    @property
    def environment(self):
        return {
            "TARGET_IMAGE": self.target_image,
            "DOCKERFILE": "/Dockerfile",
            "CONTEXT": "/workspace",
        }

    def execute(self):
        self.execution = client.containers.run(self.sut_image_tag, environment=self.environment)

# THINGS NEEDED TO RUN THIS:
#  - target image name
#  - Dockerfile
#  - build context
#
# THINGS PROVIDED BY THIS IMAGE:
#  - target image tag
#  - output docker image
#  - docker push
