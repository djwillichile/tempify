"""Tests para tempify.api — capa ergonómica tipo terra (v0.1.6)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import rioxarray  # noqa: F401
import xarray as xr

pytest.importorskip("matplotlib", reason="matplotlib no instalado; omitiendo tests de api")

import matplotlib
matplotlib.use("Agg")


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def monthly_geotiff(tmp_path: Path) -> Path:
    """GeoTIFF de 12 bandas, 4×4 px, EPSG:4326. Ciclo anual sintético."""
    rng = np.random.default_rng(0)
    months = np.arange(12).reshape(12, 1, 1)
    base = 15.0 + 10.0 * np.sin(2 * np.pi * months / 12)
    arr = (base + rng.normal(0, 0.5, (12, 4, 4))).astype(np.float32)
    da = xr.DataArray(
        arr,
        dims=("band", "y", "x"),
        coords={
            "band": list(range(1, 13)),
            "y": [3.5, 2.5, 1.5, 0.5],
            "x": [0.5, 1.5, 2.5, 3.5],
        },
        name="tavg",
    ).rio.write_crs("EPSG:4326")
    path = tmp_path / "monthly_12band.tif"
    da.rio.to_raster(path)
    return path


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

class TestImports:
    def test_import_toplevel(self) -> None:
        from tempify import plot, rast, tempify  # noqa: F401

        assert callable(rast)
        assert callable(tempify)
        assert callable(plot)


# ---------------------------------------------------------------------------
# rast()
# ---------------------------------------------------------------------------

class TestRast:
    def test_rast_returns_tempifyrast(self, monthly_geotiff: Path) -> None:
        from tempify import rast
        from tempify.api import TempifyRast

        r = rast(monthly_geotiff)
        assert isinstance(r, TempifyRast)

    def test_rast_data_is_dataarray(self, monthly_geotiff: Path) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        assert isinstance(r.data, xr.DataArray)

    def test_rast_data_identity(self, monthly_geotiff: Path) -> None:
        """r.data no debe crear una copia en cada acceso."""
        from tempify import rast

        r = rast(monthly_geotiff)
        assert r.data is r.data

    def test_rast_shape_has_12_bands(self, monthly_geotiff: Path) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        assert r.shape[0] == 12

    def test_rast_missing_file_raises(self, tmp_path: Path) -> None:
        from tempify import rast

        with pytest.raises(FileNotFoundError, match="no_existe"):
            rast(tmp_path / "no_existe.tif")


# ---------------------------------------------------------------------------
# TempifyRast repr / str
# ---------------------------------------------------------------------------

class TestTempifyRast:
    def test_repr_contains_clase_field(self, monthly_geotiff: Path) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        text = repr(r)
        assert "clase" in text or "dimensiones" in text

    def test_repr_is_string(self, monthly_geotiff: Path) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        assert isinstance(repr(r), str)
        assert len(repr(r)) > 0

    def test_str_method_prints_output(self, monthly_geotiff: Path, capsys: pytest.CaptureFixture) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        r.str()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_shape_property_is_tuple(self, monthly_geotiff: Path) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        assert isinstance(r.shape, tuple)
        assert len(r.shape) == 3

    def test_crs_property_returns_value(self, monthly_geotiff: Path) -> None:
        from tempify import rast

        r = rast(monthly_geotiff)
        crs = r.crs
        assert crs is not None  # GeoTIFF con EPSG:4326

    def test_str_on_data_without_attrs(self, capsys: pytest.CaptureFixture) -> None:
        from tempify.api import TempifyRast

        da = xr.DataArray(
            np.ones((12, 3, 3), dtype=np.float32),
            dims=("band", "y", "x"),
            coords={"band": list(range(1, 13)), "y": [2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5]},
        )
        r = TempifyRast(da)
        r.str()
        captured = capsys.readouterr()
        assert "rango" in captured.out


# ---------------------------------------------------------------------------
# plot()
# ---------------------------------------------------------------------------

class TestPlot:
    def test_plot_all_bands_no_error(self, monthly_geotiff: Path) -> None:
        import matplotlib.pyplot as plt

        from tempify import plot, rast

        r = rast(monthly_geotiff)
        plot(r)
        plt.close("all")

    def test_plot_sub_range_no_error(self, monthly_geotiff: Path) -> None:
        import matplotlib.pyplot as plt

        from tempify import plot, rast

        r = rast(monthly_geotiff)
        plot(r, sub=range(1, 4))
        plt.close("all")

    def test_plot_sub_exceeds_bands_no_error(self, monthly_geotiff: Path) -> None:
        """Índices que exceden el total de bandas deben recortarse silenciosamente."""
        import matplotlib.pyplot as plt

        from tempify import plot, rast

        r = rast(monthly_geotiff)
        plot(r, sub=range(1, 1000))
        plt.close("all")

    def test_plot_accepts_dataarray(self, monthly_geotiff: Path) -> None:
        import matplotlib.pyplot as plt

        from tempify import plot, rast

        r = rast(monthly_geotiff)
        plot(r.data)
        plt.close("all")

    def test_plot_2d_single_band_no_error(self) -> None:
        """DataArray 2D sin dimensión de stack (caso único)."""
        import matplotlib.pyplot as plt

        from tempify import plot

        da = xr.DataArray(
            np.ones((4, 4), dtype=np.float32),
            dims=("y", "x"),
            coords={"y": [3.5, 2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5, 3.5]},
        )
        plot(da)
        plt.close("all")

    def test_plot_sub_all_out_of_range(self, monthly_geotiff: Path) -> None:
        """sub con todos los índices fuera de rango → sin paneles, sin error."""
        import matplotlib.pyplot as plt

        from tempify import plot, rast

        r = rast(monthly_geotiff)
        plot(r, sub=range(100, 200))  # todos fuera de [1, 12]
        plt.close("all")


# ---------------------------------------------------------------------------
# tempify()
# ---------------------------------------------------------------------------

class TestTempify:
    def test_tempify_returns_tempifyrast(self, monthly_geotiff: Path) -> None:
        from tempify import rast, tempify
        from tempify.api import TempifyRast

        r = rast(monthly_geotiff)
        r2 = tempify(r, from_freq="monthly", to_freq="daily", year=2023)
        assert isinstance(r2, TempifyRast)

    def test_tempify_monthly_to_daily_shape(self, monthly_geotiff: Path) -> None:
        from tempify import rast, tempify

        r = rast(monthly_geotiff)
        r2 = tempify(r, from_freq="monthly", to_freq="daily", year=2023)
        assert r2.shape[0] == 365  # 2023 no es bisiesto

    def test_tempify_result_has_time_dim(self, monthly_geotiff: Path) -> None:
        from tempify import rast, tempify

        r = rast(monthly_geotiff)
        r2 = tempify(r, from_freq="monthly", to_freq="daily", year=2023)
        assert "time" in r2.data.dims

    def test_tempify_cubic_method(self, monthly_geotiff: Path) -> None:
        from tempify import rast, tempify

        r = rast(monthly_geotiff)
        r2 = tempify(r, from_freq="monthly", to_freq="daily", method="cubic", year=2023)
        assert r2.shape[0] == 365

    def test_tempify_invalid_method_raises(self, monthly_geotiff: Path) -> None:
        from tempify import rast, tempify

        r = rast(monthly_geotiff)
        with pytest.raises(ValueError, match="method"):
            tempify(r, from_freq="monthly", to_freq="daily", method="metodo_inexistente")

    def test_tempify_default_year(self, monthly_geotiff: Path) -> None:
        """year=None debe usar el año actual sin error."""
        from tempify import rast, tempify

        r = rast(monthly_geotiff)
        r2 = tempify(r, from_freq="monthly", to_freq="daily")
        assert r2.shape[0] in (365, 366)  # año actual, bisiesto o no

    def test_tempify_accepts_dataarray(self, monthly_geotiff: Path) -> None:
        """tempify() acepta xr.DataArray directamente además de TempifyRast."""
        from tempify import rast, tempify

        r = rast(monthly_geotiff)
        r2 = tempify(r.data, from_freq="monthly", to_freq="daily", year=2023)
        assert r2.shape[0] == 365


# ---------------------------------------------------------------------------
# Flujo completo (REQ-NFR-001)
# ---------------------------------------------------------------------------

class TestFullWorkflow:
    def test_full_workflow(self, monthly_geotiff: Path, capsys: pytest.CaptureFixture) -> None:
        import matplotlib.pyplot as plt

        from tempify import plot, rast, tempify

        r = rast(monthly_geotiff)
        print(r)
        r.str()
        plot(r)

        r2 = tempify(r, from_freq="monthly", to_freq="daily", method="cubic", year=2023)
        print(r2)
        r2.str()
        plot(r2, sub=range(1, 17))

        plt.close("all")
        assert r2.shape[0] == 365
        captured = capsys.readouterr()
        assert len(captured.out) > 0
