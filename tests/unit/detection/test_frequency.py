"""Tests for the temporal frequency resolver."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from tempify.detection.frequency import (
    ChelsaParser,
    ChirpsParser,
    Era5Parser,
    FrequencyParserRegistry,
    FrequencyResolutionError,
    ResolutionTier,
    TemporalFrequency,
    TemporalFrequencyResolver,
    WorldClimParser,
)


class TestParsers:
    def test_worldclim_monthly(self) -> None:
        r = WorldClimParser().parse("wc2.1_2.5m_tavg_07.tif")
        assert r is not None
        assert r.frequency == "climatological"
        assert r.month_of_year == 7
        assert r.confidence == 0.9

    def test_worldclim_invalid_returns_none(self) -> None:
        assert WorldClimParser().parse("random.tif") is None

    def test_chelsa_monthly_year(self) -> None:
        r = ChelsaParser().parse("CHELSA_tas_2015_07_V.2.1.tif")
        assert r is not None
        assert r.frequency == "monthly"
        assert r.year == 2015
        assert r.month_of_year == 7
        assert r.time_point == datetime(2015, 7, 15)

    def test_chirps_daily(self) -> None:
        r = ChirpsParser().parse("chirps-v2.0.2015.03.15.tif")
        assert r is not None
        assert r.frequency == "daily"
        assert r.time_point == datetime(2015, 3, 15)

    def test_chirps_monthly_without_day(self) -> None:
        r = ChirpsParser().parse("chirps-v2.0.2015.03.tif")
        assert r is not None
        assert r.frequency == "monthly"
        assert r.month_of_year == 3

    def test_era5_hourly(self) -> None:
        r = Era5Parser().parse("era5_t2m_20230315_12.nc")
        assert r is not None
        assert r.frequency == "hourly"
        assert r.time_point == datetime(2023, 3, 15, 12)
        assert r.confidence == 0.9

    def test_era5_daily(self) -> None:
        r = Era5Parser().parse("era5_t2m_20230315.nc")
        assert r is not None
        assert r.frequency == "daily"
        assert r.confidence == 0.85


class TestRegistry:
    def test_default_registry_has_four_parsers(self) -> None:
        registry = FrequencyParserRegistry()
        names = [p.name for p in registry.iter_parsers()]
        assert sorted(names) == ["chelsa", "chirps", "era5", "worldclim"]

    def test_register_custom_parser(self) -> None:
        registry = FrequencyParserRegistry()
        n_before = len(list(registry.iter_parsers()))
        registry.register(WorldClimParser())
        n_after = len(list(registry.iter_parsers()))
        assert n_after == n_before + 1

    def test_parse_returns_all_matches(self) -> None:
        registry = FrequencyParserRegistry()
        matches = registry.parse("wc2.1_2.5m_tavg_07.tif")
        assert len(matches) >= 1
        assert any(name == "worldclim" for name, _ in matches)


class TestResolver:
    def _files(self, names: list[str]) -> list[Path]:
        return [Path(n) for n in names]

    def test_override_wins(self) -> None:
        resolver = TemporalFrequencyResolver()
        result = resolver.resolve(
            self._files(["a.tif"]),
            override=TemporalFrequency.WEEKLY,
        )
        assert result.frequency == TemporalFrequency.WEEKLY
        assert result.tier_used == ResolutionTier.USER_OVERRIDE
        assert result.confidence == 1.0

    def test_cf_metadata_wins_over_filename(self) -> None:
        resolver = TemporalFrequencyResolver()
        files = self._files([f"wc2.1_2.5m_tavg_{m:02d}.tif" for m in range(1, 13)])
        result = resolver.resolve(files, cf_frequency=TemporalFrequency.MONTHLY)
        assert result.frequency == TemporalFrequency.MONTHLY
        assert result.tier_used == ResolutionTier.CF_METADATA

    def test_worldclim_inferred_climatological(self) -> None:
        resolver = TemporalFrequencyResolver()
        files = self._files([f"wc2.1_2.5m_tavg_{m:02d}.tif" for m in range(1, 13)])
        result = resolver.resolve(files)
        assert result.frequency == TemporalFrequency.CLIMATOLOGICAL
        assert result.tier_used == ResolutionTier.FILENAME_PATTERN

    def test_chelsa_inferred_monthly_with_time_axis(self) -> None:
        resolver = TemporalFrequencyResolver()
        files = self._files([f"CHELSA_tas_2015_{m:02d}_V.2.1.tif" for m in range(1, 13)])
        result = resolver.resolve(files)
        assert result.frequency == TemporalFrequency.MONTHLY
        assert result.time_axis is not None
        assert len(result.time_axis) == 12

    def test_count_heuristic_n_12_falls_back_when_no_filename_match(self) -> None:
        resolver = TemporalFrequencyResolver()
        files = self._files([f"random_{i}.tif" for i in range(12)])
        result = resolver.resolve(files)
        assert result.tier_used == ResolutionTier.COUNT_HEURISTIC
        assert result.frequency == TemporalFrequency.CLIMATOLOGICAL

    def test_count_heuristic_n_365_is_daily(self) -> None:
        resolver = TemporalFrequencyResolver()
        files = self._files([f"random_{i:03d}.tif" for i in range(365)])
        result = resolver.resolve(files)
        assert result.tier_used == ResolutionTier.COUNT_HEURISTIC
        assert result.frequency == TemporalFrequency.DAILY

    def test_callback_used_when_all_else_fails(self) -> None:
        called: list[TemporalFrequency] = []

        def cb(files: tuple[Path, ...]) -> TemporalFrequency:
            called.append(TemporalFrequency.WEEKLY)
            return TemporalFrequency.WEEKLY

        resolver = TemporalFrequencyResolver(callback=cb)
        files = self._files([f"random_{i}.tif" for i in range(7)])  # not 12/24/52/365/366
        result = resolver.resolve(files)
        assert result.tier_used == ResolutionTier.INTERACTIVE_CALLBACK
        assert result.frequency == TemporalFrequency.WEEKLY
        assert called == [TemporalFrequency.WEEKLY]

    def test_unresolvable_raises(self) -> None:
        resolver = TemporalFrequencyResolver()
        files = self._files([f"random_{i}.tif" for i in range(7)])
        with pytest.raises(FrequencyResolutionError):
            resolver.resolve(files)

    def test_empty_files_raises(self) -> None:
        resolver = TemporalFrequencyResolver()
        with pytest.raises(ValueError, match="non-empty"):
            resolver.resolve([])
