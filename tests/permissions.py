from collections import defaultdict

from django_pat import permissions


class MockBackend(permissions.Backend):
    def __init__(self):
        self._permissions = defaultdict(set)

    def add_permission(self, token, permission: str):
        self._permissions[token].add(permission)

    def remove_permission(self, token, permission: str):
        self._permissions[token].remove(permission)

    def has_any_permission(self, token, *permissions: str) -> bool:
        return bool(set(permissions).intersection(self._permissions.get(token) or []))
