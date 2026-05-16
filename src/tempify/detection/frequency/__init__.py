"""Temporal frequency resolver (Capa 2 sub-componente).

Resolves the temporal frequency of an input by applying a hierarchical
strategy: CF-conventions metadata → filename pattern (WorldClim,
CHELSA, CHIRPS, ERA5) → count heuristic → interactive callback.

When filenames encode dates, the resolver also extracts the canonical
``time_axis`` (per ADR-0015 midpoint convention) so the pipeline can
stamp accurate timestamps in the output.
"""

from tempify.detection.frequency.parsers import (
    BaseFilenameParser,
    ChelsaParser,
    ChirpsParser,
    Era5Parser,
    FrequencyParserRegistry,
    ParseResult,
    WorldClimParser,
)
from tempify.detection.frequency.resolver import (
    FrequencyResolutionError,
    ResolutionResult,
    ResolutionTier,
    TemporalFrequency,
    TemporalFrequencyResolver,
)

__all__ = [
    "BaseFilenameParser",
    "ChelsaParser",
    "ChirpsParser",
    "Era5Parser",
    "FrequencyParserRegistry",
    "FrequencyResolutionError",
    "ParseResult",
    "ResolutionResult",
    "ResolutionTier",
    "TemporalFrequency",
    "TemporalFrequencyResolver",
    "WorldClimParser",
]
