"""Temporal frequency resolver.

Applies the four-tier hierarchy described in
``specs/temporal-frequency-resolver/requirements.md``:

1. CF metadata (when an ``xarray.Dataset`` is supplied with a ``time``
   coordinate carrying CF units/calendar).
2. Filename pattern matching against registered parsers.
3. Count heuristic over the number of input files.
4. User callback (when registered).

If higher-tier results conflict among themselves, the higher tier wins
and the conflict is annotated in ``ResolutionResult.source_evidence``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from tempify.detection.frequency.parsers import (
    FrequencyParserRegistry,
    ParseResult,
)


class TemporalFrequency(StrEnum):
    """Canonical temporal frequencies recognised by tempify v0.1.0."""

    MONTHLY = "monthly"
    DAILY = "daily"
    WEEKLY = "weekly"
    HOURLY = "hourly"
    YEARLY = "yearly"
    CLIMATOLOGICAL = "climatological"


class ResolutionTier(StrEnum):
    """Tier that produced the resolution (per ADR-0008)."""

    CF_METADATA = "cf_metadata"
    FILENAME_PATTERN = "filename_pattern"
    COUNT_HEURISTIC = "count_heuristic"
    INTERACTIVE_CALLBACK = "interactive_callback"
    USER_OVERRIDE = "user_override"


TIER_BASE_CONFIDENCE: dict[ResolutionTier, float] = {
    ResolutionTier.CF_METADATA: 1.0,
    ResolutionTier.FILENAME_PATTERN: 0.9,
    ResolutionTier.COUNT_HEURISTIC: 0.7,
    ResolutionTier.INTERACTIVE_CALLBACK: 0.4,
    ResolutionTier.USER_OVERRIDE: 1.0,
}


class FrequencyResolutionError(Exception):
    """Raised when no tier can resolve the temporal frequency."""

    code: ClassVar[str] = "TEMPIFY-DET-FREQ-001"

    def __init__(self, partial_evidence: str) -> None:
        self.partial_evidence = partial_evidence
        super().__init__(
            f"No se pudo inferir la frecuencia temporal de los inputs. "
            f"Evidencia parcial: {partial_evidence}. "
            "Provea un callback interactivo o use --frequency en la CLI."
        )


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    """Outcome of :meth:`TemporalFrequencyResolver.resolve`."""

    frequency: TemporalFrequency
    tier_used: ResolutionTier
    confidence: float
    source_evidence: str
    time_axis: tuple[datetime, ...] | None = field(default=None)
    calendar_agnostic: bool = field(default=False)


class TemporalFrequencyResolver:
    """Resolve temporal frequency from file inputs or CF metadata."""

    def __init__(
        self,
        registry: FrequencyParserRegistry | None = None,
        callback: Callable[[tuple[Path, ...]], TemporalFrequency] | None = None,
    ) -> None:
        self.registry = registry or FrequencyParserRegistry()
        self.callback = callback

    def resolve(
        self,
        files: tuple[Path, ...] | list[Path],
        cf_frequency: TemporalFrequency | None = None,
        override: TemporalFrequency | None = None,
    ) -> ResolutionResult:
        """Resolve the frequency for ``files``.

        Parameters
        ----------
        files : tuple[Path, ...] | list[Path]
            Ordered list of input files. Must be non-empty.
        cf_frequency : TemporalFrequency | None
            When the caller already knows the frequency from CF metadata
            (e.g., an ``xarray.Dataset.time`` decoded by CF), pass it
            here. This becomes Tier 1 evidence.
        override : TemporalFrequency | None
            User-supplied override (e.g., CLI ``--frequency``). Wins
            over every other tier.
        """
        files_t = tuple(Path(p) for p in files)
        if not files_t:
            raise ValueError("files must be non-empty")
        evidence: list[str] = []

        if override is not None:
            return ResolutionResult(
                frequency=override,
                tier_used=ResolutionTier.USER_OVERRIDE,
                confidence=TIER_BASE_CONFIDENCE[ResolutionTier.USER_OVERRIDE],
                source_evidence="override del usuario",
            )

        if cf_frequency is not None:
            return ResolutionResult(
                frequency=cf_frequency,
                tier_used=ResolutionTier.CF_METADATA,
                confidence=TIER_BASE_CONFIDENCE[ResolutionTier.CF_METADATA],
                source_evidence=f"metadata CF declara frecuencia '{cf_frequency.value}'",
            )

        # Tier 2: filename pattern parsing
        per_file_matches: list[list[tuple[str, ParseResult]]] = []
        for p in files_t:
            per_file_matches.append(self.registry.parse(p.name))

        any_match = any(matches for matches in per_file_matches)
        if any_match:
            freqs: list[str] = []
            parser_names: list[str] = []
            time_points: list[datetime] = []
            for matches in per_file_matches:
                if not matches:
                    continue
                parser_name, best = max(matches, key=lambda pair: pair[1].confidence)
                freqs.append(best.frequency)
                parser_names.append(parser_name)
                if best.time_point is not None:
                    time_points.append(best.time_point)
            if len(set(freqs)) == 1:
                inferred = TemporalFrequency(freqs[0])
                time_axis = tuple(sorted(time_points)) if time_points else None
                return ResolutionResult(
                    frequency=inferred,
                    tier_used=ResolutionTier.FILENAME_PATTERN,
                    confidence=TIER_BASE_CONFIDENCE[ResolutionTier.FILENAME_PATTERN],
                    source_evidence=(
                        f"parser '{parser_names[0]}' identificó frecuencia "
                        f"'{inferred.value}' en {len(freqs)}/{len(files_t)} archivos"
                    ),
                    time_axis=time_axis,
                    calendar_agnostic=(time_axis is None),
                )
            evidence.append(f"parsers detectaron frecuencias mixtas: {sorted(set(freqs))}")

        # Tier 3: count heuristic
        n = len(files_t)
        heuristic = _heuristic_frequency_from_count(n)
        if heuristic is not None:
            return ResolutionResult(
                frequency=heuristic,
                tier_used=ResolutionTier.COUNT_HEURISTIC,
                confidence=TIER_BASE_CONFIDENCE[ResolutionTier.COUNT_HEURISTIC],
                source_evidence=(f"heurística por conteo: {n} archivos → {heuristic.value}"),
                calendar_agnostic=True,
            )

        # Tier 3.b: band-count heuristic for a single multi-band file
        if n == 1:
            band_count = _probe_band_count(files_t[0])
            if band_count is not None:
                by_bands = _heuristic_frequency_from_count(band_count)
                if by_bands is not None:
                    return ResolutionResult(
                        frequency=by_bands,
                        tier_used=ResolutionTier.COUNT_HEURISTIC,
                        confidence=TIER_BASE_CONFIDENCE[ResolutionTier.COUNT_HEURISTIC],
                        source_evidence=(
                            f"heurística por bandas: 1 archivo con {band_count} bandas → "
                            f"{by_bands.value}"
                        ),
                        calendar_agnostic=True,
                    )
                evidence.append(
                    f"archivo multibanda con {band_count} bandas (no canónico)"
                )
            else:
                evidence.append(f"conteo de archivos N={n} sin frecuencia canónica")
        else:
            evidence.append(f"conteo de archivos N={n} sin frecuencia canónica")

        # Tier 4: interactive callback
        if self.callback is not None:
            chosen = self.callback(files_t)
            return ResolutionResult(
                frequency=chosen,
                tier_used=ResolutionTier.INTERACTIVE_CALLBACK,
                confidence=TIER_BASE_CONFIDENCE[ResolutionTier.INTERACTIVE_CALLBACK],
                source_evidence=(f"callback interactivo retornó '{chosen.value}'"),
            )

        raise FrequencyResolutionError(partial_evidence="; ".join(evidence) or "ninguna")


def _heuristic_frequency_from_count(n: int) -> TemporalFrequency | None:
    """Map a file count to a canonical frequency. Returns ``None`` if ambiguous."""
    if n == 12:
        return TemporalFrequency.CLIMATOLOGICAL
    if n in (365, 366):
        return TemporalFrequency.DAILY
    if n == 52:
        return TemporalFrequency.WEEKLY
    if n == 24:
        return TemporalFrequency.HOURLY
    return None


def _probe_band_count(path: Path) -> int | None:
    """Probe a raster file for its band count. Returns ``None`` if it cannot be opened."""
    try:
        import rasterio  # type: ignore[import-untyped]
    except ImportError:
        return None
    try:
        with rasterio.open(path) as src:
            return int(src.count)
    except Exception:
        return None
