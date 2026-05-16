"""Tests for io-handlers Protocols and typed exceptions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import xarray as xr

from tempify.io import (
    BaseReader,
    BaseWriter,
    CRSPreservationError,
    IOTempifyError,
    MissingOptionalDependencyError,
    UnsupportedBandCountError,
    UnsupportedFormatError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(UnsupportedFormatError, IOTempifyError)
    assert issubclass(MissingOptionalDependencyError, IOTempifyError)
    assert issubclass(UnsupportedBandCountError, IOTempifyError)
    assert issubclass(CRSPreservationError, IOTempifyError)


def test_exception_codes_are_unique_and_canonical() -> None:
    codes = {
        UnsupportedFormatError.code,
        MissingOptionalDependencyError.code,
        UnsupportedBandCountError.code,
        CRSPreservationError.code,
    }
    assert len(codes) == 4
    assert all(c.startswith("TEMPIFY-IO-") for c in codes)


def test_protocols_are_runtime_checkable() -> None:
    class _DummyReader:
        def read(self, source: Path | list[Path]) -> xr.DataArray:
            return xr.DataArray([0])

        def metadata(self) -> dict[str, Any]:
            return {}

    class _DummyWriter:
        def write(self, data: xr.DataArray, target: Path, **opts: Any) -> Path | list[Path]:
            return target

    assert isinstance(_DummyReader(), BaseReader)
    assert isinstance(_DummyWriter(), BaseWriter)


def test_unsupported_format_message_in_spanish() -> None:
    err = UnsupportedFormatError("xyz")
    s = str(err)
    assert "Formato" in s
    assert "xyz" in s


def test_missing_dependency_includes_install_hint() -> None:
    err = MissingOptionalDependencyError("zarr", "zarr")
    assert "pip install tempify[zarr]" in str(err)


def test_band_count_error_carries_count() -> None:
    err = UnsupportedBandCountError(100000, 65535)
    assert err.count == 100000
    assert err.max_allowed == 65535
    assert "100000" in str(err)
