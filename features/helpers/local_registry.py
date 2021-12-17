from os.path import abspath

HTPASSWD_CONTAINER_PATH = '/htpasswd'


class LocalRegistry:
    """ Resource handle for ephemeral, test-specific docker registry """

    image = 'registry:2.7.1'

    def __init__(self, auth = False, local_port = 5000):
        self.name = "registry"
        self._env = {}
        self.local_port = local_port
        self._run()

    def _run(self):
        from . import client
        self._container = client.containers.run(self.image,
                                                name=self.name,
                                                environment=self._env,
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

    def __del__(self):
        self._container.remove(force=True)
