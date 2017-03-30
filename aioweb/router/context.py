from typing import Iterable, Callable, Text


class DefaultContext(object):
    def __init__(self, checks: Iterable[Callable] = tuple()):
        self.checks = tuple(checks) if type(checks) not in (list, tuple) else checks
        self.reason = 'Check failed'    # TODO: check function should return reason

    def check(self, request):
        if self.checks:
            for check_fn in self.checks:
                if callable(check_fn) and not check_fn(request):
                    return False
        return True


class AuthenticatedContext(DefaultContext):
    def __init__(self,
                 checks: Iterable[Callable] = None,
                 in_groups: Iterable[Text] = None,
                 has_permissions: Iterable[Text] = None):
        auth_checks = [lambda r: hasattr(r, 'user') and r.user.is_authenticated]
        if checks and type(checks) in (list, tuple):
            auth_checks.extend(checks)
        super().__init__(checks=auth_checks)
        if in_groups:
            # TODO: add group checks
            pass
        if has_permissions:
            # TODO: add permission checks
            pass

        self.reason = 'Unauthenticated'
