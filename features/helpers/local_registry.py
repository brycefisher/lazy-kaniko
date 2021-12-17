from os.path import abspath

# Bcrypted htpasswd file generated from:
# https://www.askapache.com/online-tools/htpasswd-generator/
HTPASSWD_CONTAINER_PATH = '/htpasswd'
HTPASSWD_USER = 'kaniko'
HTPASSWD_PASS = 'lazy'


class LocalRegistry:
    """ Resource handle for ephemeral, test-specific docker registry """

    image = 'registry:2.7.1'

    def __init__(self, auth = False, local_port = 5000):
        self.name = "registry"
        self._env = {}
        self._volumes = []
        self.local_port = local_port
        self.user = None
        self.password = None
        if auth:
            self.setup_auth()
        self._run()

    def _run(self):
        from . import client
        self._container = client.containers.run(self.image,
                                                name=self.name,
                                                environment=self._env,
                                                volumes=self._volumes,
                                                ports={"5000/tcp": self.local_port},
                                                detach=True)

    def setup_auth(self):
        self._volumes.append(abspath('./features/helpers/htpasswd') + ':' + HTPASSWD_CONTAINER_PATH)
        self._env["REGISTRY_AUTH"] = "htpasswd"
        self._env["REGISTRY_AUTH_HTPASSWD_REALM"] = "Docker Registry"
        self._env["REGISTRY_AUTH_HTPASSWD_PATH"] =  HTPASSWD_CONTAINER_PATH
        self.user = "kaniko"
        self.password = "lazy"

    def login(self):
        from . import client
        client.login(
            username=HTPASSWD_USER,
            password=HTPASSWD_PASS,
            registry=self.address
        )

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
