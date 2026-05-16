"""Variable profile loader and matcher.

Profiles are YAML files declaring per-variable conventions: allowed
interpolation methods, physical range, acceptable mean error, units,
aliases. They live in :mod:`tempify.profiles` and are loaded via
:func:`importlib.resources`.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from importlib import resources
from typing import Any

import yaml  # type: ignore[import-untyped]

from tempify.validation.errors import UnknownVariableProfileError

ALLOWED_METHODS: frozenset[str] = frozenset({"linear", "pchip", "pchip_mp", "fourier"})


@dataclass(frozen=True, slots=True)
class VariableProfile:
    """Declarative profile of a climatological variable.

    Loaded from a YAML file in :mod:`tempify.profiles`. The full schema
    is documented in ``docs/schemas/variable-profile.schema.yaml``.
    """

    name: str
    canonical_name: str
    units: str
    allowed_methods: tuple[str, ...]
    physical_min: float
    physical_max: float
    acceptable_mean_error: float
    aliases: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VariableProfile:
        """Build a profile from a parsed YAML payload."""
        return cls(
            name=str(data["name"]),
            canonical_name=str(data.get("canonical_name", data["name"])),
            units=str(data["units"]),
            allowed_methods=tuple(data.get("allowed_methods", [])),
            physical_min=float(data["physical_range"]["min"]),
            physical_max=float(data["physical_range"]["max"]),
            acceptable_mean_error=float(data["acceptable_mean_error"]),
            aliases=tuple(data.get("aliases", [])),
            description=str(data.get("description", "")),
        )


def _read_profile_yaml(filename: str) -> VariableProfile:
    """Load a single profile YAML from the tempify.profiles package."""
    with resources.files("tempify.profiles").joinpath(filename).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return VariableProfile.from_dict(data)


def iter_builtin_profiles() -> Iterator[VariableProfile]:
    """Yield every built-in variable profile bundled with tempify."""
    for entry in resources.files("tempify.profiles").iterdir():
        name = entry.name
        if not name.endswith(".yaml") or name.startswith("_"):
            continue
        yield _read_profile_yaml(name)


class VariableProfileMatcher:
    """Look up a :class:`VariableProfile` by name or alias (case-insensitive)."""

    def __init__(self, profiles: list[VariableProfile] | None = None) -> None:
        self._profiles = profiles if profiles is not None else list(iter_builtin_profiles())

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(p.name for p in self._profiles))

    def match(self, query: str) -> VariableProfile:
        """Return the profile whose name or alias matches ``query``."""
        q = query.lower().strip()
        for p in self._profiles:
            if p.name.lower() == q:
                return p
            if any(a.lower() == q for a in p.aliases):
                return p
        raise UnknownVariableProfileError(name=query, available=self.names())
