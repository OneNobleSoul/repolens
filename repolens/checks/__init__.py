"""Built-in check suite.

Importing :func:`all_checks` returns every registered check. Individual
check modules register themselves via the ``@register`` decorator.
"""

from .base import Check, all_checks, register

__all__ = ["Check", "all_checks", "register"]
