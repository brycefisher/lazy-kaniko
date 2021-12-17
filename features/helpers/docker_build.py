from os.path import abspath
import json


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



