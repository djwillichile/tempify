"""Tests del módulo tempify.plotting (v0.1.5).

matplotlib es dependencia opcional; los tests se omiten si no está instalada.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

pytest.importorskip("matplotlib", reason="matplotlib no instalado; omitiendo tests de plotting")


@pytest.fixture(scope="module")
def sample_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Muestra sintética 10×10 px, compartida en todos los tests de plotting."""
    from tempify.datasets import create_worldclim_like_sample

    tmp = tmp_path_factory.mktemp("plotting_data")
    return create_worldclim_like_sample(tmp / "data", n_pixels=10, overwrite=True)


@pytest.fixture(scope="module")
def daily_sample() -> xr.DataArray:
    """DataArray diario mínimo para 2023 (365, 4, 4)."""
    times = pd.date_range("2023-01-01", periods=365, freq="D")
    data = (np.random.default_rng(42).random((365, 4, 4)) * 20 + 5).astype(np.float32)
    return xr.DataArray(data, dims=("time", "y", "x"), coords={"time": times}, name="tavg")


@pytest.fixture(scope="module")
def monthly_sample() -> xr.DataArray:
    """DataArray mensual mínimo (12, 4, 4)."""
    data = (np.random.default_rng(42).random((12, 4, 4)) * 20 + 5).astype(np.float32)
    return xr.DataArray(
        data, dims=("month", "y", "x"), coords={"month": list(range(1, 13))}, name="tavg"
    )


class TestPlotMonthlyRasters:
    """plot_monthly_rasters() — grilla 3×4 de GeoTIFFs mensuales."""

    def test_retorna_fig_y_axes(self, sample_data_dir: Path) -> None:
        import matplotlib
        import matplotlib.figure

        matplotlib.use("Agg")
        from tempify.plotting import plot_monthly_rasters

        fig, axes = plot_monthly_rasters(sample_data_dir)
        assert isinstance(fig, matplotlib.figure.Figure)
        assert axes is not None

    def test_guarda_png_cuando_se_entrega_output_path(
        self, sample_data_dir: Path, tmp_path: Path
    ) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_monthly_rasters

        out = tmp_path / "monthly.png"
        fig, _ = plot_monthly_rasters(sample_data_dir, output_path=out)
        plt.close(fig)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_acepta_titulo(self, sample_data_dir: Path) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_monthly_rasters

        fig, _ = plot_monthly_rasters(sample_data_dir, title="Título de prueba")
        plt.close(fig)


class TestPlotRasterTimeseries:
    """plot_raster_timeseries() — serie diaria de un píxel con anclas opcionales."""

    def test_retorna_fig_y_ax(self, daily_sample: xr.DataArray) -> None:
        import matplotlib
        import matplotlib.figure

        matplotlib.use("Agg")
        from tempify.plotting import plot_raster_timeseries

        fig, ax = plot_raster_timeseries(daily_sample)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_con_input_mensual(
        self, daily_sample: xr.DataArray, monthly_sample: xr.DataArray
    ) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_raster_timeseries

        fig, ax = plot_raster_timeseries(daily_sample, monthly_input=monthly_sample)
        plt.close(fig)

    def test_guarda_archivo(
        self, daily_sample: xr.DataArray, tmp_path: Path
    ) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_raster_timeseries

        out = tmp_path / "timeseries.png"
        fig, _ = plot_raster_timeseries(daily_sample, output_path=out)
        plt.close(fig)
        assert out.exists()

    def test_acepta_pixel_yx(self, daily_sample: xr.DataArray) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_raster_timeseries

        fig, _ = plot_raster_timeseries(daily_sample, pixel_yx=(0, 0))
        plt.close(fig)


class TestPlotTemporalStack3d:
    """plot_temporal_stack_3d() — capas ráster apiladas en 3D."""

    def test_retorna_fig(self, daily_sample: xr.DataArray) -> None:
        import matplotlib
        import matplotlib.figure

        matplotlib.use("Agg")
        from tempify.plotting import plot_temporal_stack_3d

        fig, ax = plot_temporal_stack_3d(daily_sample, months=[6, 7], days=(15,))
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_guarda_archivo(
        self, daily_sample: xr.DataArray, tmp_path: Path
    ) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_temporal_stack_3d

        out = tmp_path / "stack3d.png"
        fig, _ = plot_temporal_stack_3d(
            daily_sample, months=[6, 7], days=(15,), output_path=out
        )
        plt.close(fig)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_acepta_flags_show_en_false(self, daily_sample: xr.DataArray) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        from tempify.plotting import plot_temporal_stack_3d

        fig, _ = plot_temporal_stack_3d(
            daily_sample,
            months=[6],
            days=(15,),
            show_title=False,
            show_legend=False,
            show_colorbar=False,
        )
        plt.close(fig)


class TestMensajeErrorSinMatplotlib:
    """_require_matplotlib() debe lanzar ImportError con instrucción de instalación."""

    def test_lanza_import_error_con_hint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import importlib
        import sys

        monkeypatch.setitem(sys.modules, "matplotlib", None)  # type: ignore[arg-type]

        import tempify.plotting as pm

        importlib.reload(pm)
        with pytest.raises(ImportError, match="pip install tempify\\[viz\\]"):
            pm._require_matplotlib()
