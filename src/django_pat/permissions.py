from typing import Dict
from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string


class Backend:
    def has_permission(self, token, permission: str) -> bool:
        raise NotImplementedError()


class UserBackend(Backend):
    def has_permission(self, token, permission: str) -> bool:
        """
        Determine if the given token has been provided access to do the requested action.
        """
        return token.user.has_perm(permission)


class ConfigurationError(ValueError):
    pass


def load_backend(path):
    return import_string(path)()


class BackendManager:
    instance = None
    _backends: Optional[Dict[str, Backend]]

    def __new__(cls, *args, **kwargs):
        # WIP implements singleton pattern, but I should verify it works the way I want.
        if cls.instance is not None:
            return cls.instance
        else:
            inst = cls.instance = super().__new__(cls, *args, **kwargs)
            inst._backends = None
            return inst

    def clear_cache(self):
        self._backends = None

    def get_backends(self) -> Dict[str, Backend]:
        if self._backends is not None:
            return self._backends

        backends: Dict[str, Backend] = {}

        # WIP Handle poorly defined dicts

        for k, d in settings.PAT_PERMISSIONS.items():  # type: ignore
            backends[k] = load_backend(d["backend"])

        self._backends = backends
        return self._backends

    def get_backend(self, name: str = None) -> Backend:
        if name is None:
            name = settings.PAT_PERMISSIONS_DEFAULT  # type: ignore

        b = self.get_backends().get(name)

        if b is None:
            raise ConfigurationError(f"Backend {name} is not configured.")

        return b


def manager() -> BackendManager:
    return BackendManager()


def get_backend(name: str = None) -> Backend:
    # WIP I'd love to instead be able to call `manager` as a property, but still have it be lazy...
    return manager().get_backend(name)


def clear_cache():
    return manager().clear_cache()
