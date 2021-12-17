from dataclasses import dataclass
import os


@dataclass
class RemoteRegistry:
    address: str
    user: str
    password: str

    def from_env():
        return RemoteRegistry(
            address=os.environ["REGISTRY_URL"],
            user=os.environ["REGISTRY_USER"],
            password=os.environ["REGISTRY_PASS"],
        )

    def login(self):
        from . import client
        client.login(
            username=self.user,
            password=self.password,
            registry=self.address
        )

    @property
    def local_address(self):
        return self.address
