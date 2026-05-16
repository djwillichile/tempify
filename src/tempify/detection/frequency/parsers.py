"""Filename parsers for canonical climate datasets.

Each parser knows how to recognise a specific naming convention
(WorldClim, CHELSA, CHIRPS, ERA5) and extract from a filename the
month, year, day, hour and inferred temporal frequency. New parsers can
be registered via :class:`FrequencyParserRegistry`.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class ParseResult:
    """Output of a :class:`BaseFilenameParser`.

    Attributes
    ----------
    frequency : str
        One of the values of :class:`~tempify.detection.frequency.resolver.TemporalFrequency`.
    confidence : float
        Match quality in [0.0, 1.0].
    time_point : datetime | None
        Single datetime extracted from the filename, if applicable.
    time_range : tuple[datetime, datetime] | None
        Inclusive range extracted from the filename, if applicable.
    month_of_year : int | None
        Month in [1, 12] when the filename encodes only the month-of-year.
    year : int | None
        Year extracted from the filename when present.
    band_index : int | None
        Index of the band in a multi-band GeoTIFF when applicable.
    """

    frequency: str
    confidence: float
    time_point: datetime | None = None
    time_range: tuple[datetime, datetime] | None = None
    month_of_year: int | None = None
    year: int | None = None
    band_index: int | None = None


class BaseFilenameParser(ABC):
    """Abstract base class for filename-driven frequency parsers."""

    name: ClassVar[str] = "base"
    confidence: ClassVar[float] = 0.5

    @abstractmethod
    def parse(self, filename: str) -> ParseResult | None:
        """Return a :class:`ParseResult` if ``filename`` matches, else ``None``."""


_WORLDCLIM_MONTHLY = re.compile(
    r"^wc(?P<version>[\d.]+)?_(?P<res>[a-z0-9.]+)_(?P<var>[a-z]+)_(?P<month>\d{2})\.tif$",
    re.IGNORECASE,
)


class WorldClimParser(BaseFilenameParser):
    """Parser for WorldClim v2.x filenames (monthly climatology)."""

    name = "worldclim"
    confidence = 0.9

    def parse(self, filename: str) -> ParseResult | None:
        m = _WORLDCLIM_MONTHLY.match(filename)
        if not m:
            return None
        month = int(m.group("month"))
        if not 1 <= month <= 12:
            return None
        return ParseResult(
            frequency="climatological",
            confidence=self.confidence,
            month_of_year=month,
        )


_CHELSA_MONTHLY = re.compile(
    r"^CHELSA_(?P<var>[a-z]+)_(?P<year>\d{4})_(?P<month>\d{2})_V[\d.]+\.tif$",
    re.IGNORECASE,
)


class ChelsaParser(BaseFilenameParser):
    """Parser for CHELSA v2 monthly filenames."""

    name = "chelsa"
    confidence = 0.9

    def parse(self, filename: str) -> ParseResult | None:
        m = _CHELSA_MONTHLY.match(filename)
        if not m:
            return None
        year = int(m.group("year"))
        month = int(m.group("month"))
        if not 1 <= month <= 12:
            return None
        return ParseResult(
            frequency="monthly",
            confidence=self.confidence,
            time_point=datetime(year, month, 15),
            month_of_year=month,
            year=year,
        )


_CHIRPS = re.compile(
    r"^chirps-v(?P<version>[\d.]+)\."
    r"(?P<year>\d{4})\."
    r"(?P<month>\d{2})"
    r"(?:\.(?P<day>\d{2}))?"
    r"\.(?:tif|tiff|nc)$",
    re.IGNORECASE,
)


class ChirpsParser(BaseFilenameParser):
    """Parser for CHIRPS daily and monthly filenames."""

    name = "chirps"
    confidence = 0.9

    def parse(self, filename: str) -> ParseResult | None:
        m = _CHIRPS.match(filename)
        if not m:
            return None
        year = int(m.group("year"))
        month = int(m.group("month"))
        if not 1 <= month <= 12:
            return None
        day = m.group("day")
        if day is not None:
            return ParseResult(
                frequency="daily",
                confidence=self.confidence,
                time_point=datetime(year, month, int(day)),
                year=year,
                month_of_year=month,
            )
        return ParseResult(
            frequency="monthly",
            confidence=self.confidence,
            time_point=datetime(year, month, 15),
            year=year,
            month_of_year=month,
        )


_ERA5 = re.compile(
    r"^era5_(?P<var>[a-z0-9_]+)_"
    r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})"
    r"(?:_(?P<hour>\d{2}))?"
    r"\.(?:nc|tif)$",
    re.IGNORECASE,
)


class Era5Parser(BaseFilenameParser):
    """Parser for ERA5 daily/hourly filenames."""

    name = "era5"
    confidence = 0.9

    def parse(self, filename: str) -> ParseResult | None:
        m = _ERA5.match(filename)
        if not m:
            return None
        year = int(m.group("year"))
        month = int(m.group("month"))
        day = int(m.group("day"))
        hour = m.group("hour")
        if not 1 <= month <= 12:
            return None
        if hour is not None:
            return ParseResult(
                frequency="hourly",
                confidence=self.confidence,
                time_point=datetime(year, month, day, int(hour)),
                year=year,
                month_of_year=month,
            )
        return ParseResult(
            frequency="daily",
            confidence=0.85,
            time_point=datetime(year, month, day),
            year=year,
            month_of_year=month,
        )


class FrequencyParserRegistry:
    """Holds the active set of :class:`BaseFilenameParser` instances."""

    def __init__(self, parsers: list[BaseFilenameParser] | None = None) -> None:
        self._parsers: list[BaseFilenameParser] = parsers or [
            WorldClimParser(),
            ChelsaParser(),
            ChirpsParser(),
            Era5Parser(),
        ]

    def register(self, parser: BaseFilenameParser) -> None:
        self._parsers.append(parser)

    def iter_parsers(self) -> Iterator[BaseFilenameParser]:
        return iter(self._parsers)

    def parse(self, filename: str) -> list[tuple[str, ParseResult]]:
        """Run every parser; return the list of ``(parser_name, result)`` matches."""
        out: list[tuple[str, ParseResult]] = []
        for p in self._parsers:
            r = p.parse(filename)
            if r is not None:
                out.append((p.name, r))
        return out
