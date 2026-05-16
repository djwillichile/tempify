"""Command-line interface for tempify (Capa 6).

Per the architectural rule, the CLI only imports from ``tempify.pipeline``;
direct imports from ``tempify.detection``, ``tempify.io``,
``tempify.interpolation`` or ``tempify.validation`` are prohibited and
checked by ``test_cli_imports_only_pipeline``.
"""

from tempify.cli.app import app

__all__ = ["app"]
