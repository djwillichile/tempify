"""Tests del módulo tempify.utils (v0.1.5)."""

from __future__ import annotations

import datetime
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
import xarray as xr


@pytest.fixture
def daily_dataarray() -> xr.DataArray:
    """DataArray diario mínimo (365, 3, 3) para 2023."""
    times = pd.date_range("2023-01-01", periods=365, freq="D")
    data = np.random.default_rng(42).random((365, 3, 3)).astype(np.float32)
    return xr.DataArray(
        data,
        dims=("time", "y", "x"),
        coords={"time": times},
        name="tavg",
    )


class TestGetAnchorDates:
    """get_anchor_dates() — retorna 12 fechas en el día 15 de cada mes."""

    def test_retorna_12_fechas(self) -> None:
        from tempify.utils import get_anchor_dates

        dates = get_anchor_dates(2023)
        assert len(dates) == 12

    def test_todas_en_dia_15(self) -> None:
        from tempify.utils import get_anchor_dates

        dates = get_anchor_dates(2023)
        assert all(d.day == 15 for d in dates)

    def test_cubre_todos_los_meses(self) -> None:
        from tempify.utils import get_anchor_dates

        dates = get_anchor_dates(2023)
        assert [d.month for d in dates] == list(range(1, 13))

    def test_retorna_objetos_date(self) -> None:
        from tempify.utils import get_anchor_dates

        dates = get_anchor_dates(2023)
        assert all(isinstance(d, datetime.date) for d in dates)

    def test_ano_correcto(self) -> None:
        from tempify.utils import get_anchor_dates

        dates = get_anchor_dates(2024)
        assert all(d.year == 2024 for d in dates)


class TestExtractDailyRasters:
    """extract_daily_rasters() — filtra DataArray diario por mes/día/año."""

    def test_filtrar_por_meses(self, daily_dataarray: xr.DataArray) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray, months=[6, 7])
        meses = set(int(m) for m in subset["time"].dt.month.values)
        assert meses == {6, 7}

    def test_filtrar_por_dias(self, daily_dataarray: xr.DataArray) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray, days=[15])
        dias = set(int(d) for d in subset["time"].dt.day.values)
        assert dias == {15}

    def test_filtrar_por_meses_y_dias(self, daily_dataarray: xr.DataArray) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray, months=[4, 5, 6], days=[5, 15, 25])
        assert len(subset["time"]) == 9  # 3 meses × 3 días

    def test_sin_filtro_retorna_todo(self, daily_dataarray: xr.DataArray) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray)
        assert len(subset["time"]) == 365

    def test_preserva_dimensiones_espaciales(self, daily_dataarray: xr.DataArray) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray, months=[1])
        assert subset.sizes["y"] == 3
        assert subset.sizes["x"] == 3

    def test_filtrar_por_ano(self, daily_dataarray: xr.DataArray) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray, year=2023)
        assert len(subset["time"]) == 365

    def test_resultado_vacio_si_ano_no_existe(
        self, daily_dataarray: xr.DataArray
    ) -> None:
        from tempify.utils import extract_daily_rasters

        subset = extract_daily_rasters(daily_dataarray, year=2099)
        assert len(subset["time"]) == 0


class TestOpenTempifyOutput:
    """open_tempify_output() — carga output del pipeline desde Path o PipelineResult."""

    def test_acepta_path_netcdf(
        self, tmp_path: Path, daily_dataarray: xr.DataArray
    ) -> None:
        from tempify.utils import open_tempify_output

        nc_path = tmp_path / "output.nc"
        daily_dataarray.to_netcdf(nc_path)
        result = open_tempify_output(nc_path)
        assert isinstance(result, xr.DataArray)

    def test_lanza_error_por_extension_desconocida(self, tmp_path: Path) -> None:
        from tempify.utils import open_tempify_output

        bad = tmp_path / "output.xyz"
        bad.touch()
        with pytest.raises(ValueError, match="Cannot determine output format"):
            open_tempify_output(bad)

    def test_acepta_pipeline_result_con_netcdf(
        self, tmp_path: Path, daily_dataarray: xr.DataArray
    ) -> None:
        from tempify.utils import open_tempify_output

        nc_path = tmp_path / "output.nc"
        daily_dataarray.to_netcdf(nc_path)

        mock_result = MagicMock()
        mock_result.outputs = (nc_path,)
        result = open_tempify_output(mock_result)
        assert isinstance(result, xr.DataArray)

    def test_lanza_error_si_outputs_vacio(self) -> None:
        from tempify.utils import open_tempify_output

        mock_result = MagicMock()
        mock_result.outputs = ()
        with pytest.raises(ValueError, match="no outputs"):
            open_tempify_output(mock_result)


class TestRasterInfo:
    """raster_info() — imprime resumen estilo terra::print(r)."""

    def test_imprime_sin_error_con_dataarray_mensual(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tempify.datasets import create_worldclim_like_sample, read_monthly_stack
        from tempify.utils import raster_info

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        stack = read_monthly_stack(out)
        raster_info(stack)
        captured = capsys.readouterr()
        assert "dimensiones" in captured.out.lower() or "dimensions" in captured.out.lower()

    def test_imprime_sin_error_con_dataarray_diario(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        import pandas as pd
        from tempify.utils import raster_info

        times = pd.date_range("2023-01-01", periods=365, freq="D")
        data = np.random.default_rng(0).random((365, 5, 5)).astype(np.float32)
        da = xr.DataArray(data, dims=("time", "y", "x"), coords={"time": times})
        raster_info(da)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_muestra_dimensiones_correctas(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from tempify.datasets import create_worldclim_like_sample, read_monthly_stack
        from tempify.utils import raster_info

        out = create_worldclim_like_sample(tmp_path / "out2", n_pixels=8, overwrite=True)
        stack = read_monthly_stack(out)
        raster_info(stack)
        captured = capsys.readouterr()
        assert "8" in captured.out  # n_pixels

    def test_muestra_crs(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        import rioxarray  # noqa: F401

        from tempify.datasets import create_worldclim_like_sample, read_monthly_stack
        from tempify.utils import raster_info

        out = create_worldclim_like_sample(tmp_path / "out3", n_pixels=8, overwrite=True)
        stack = read_monthly_stack(out)
        raster_info(stack)
        captured = capsys.readouterr()
        assert "4326" in captured.out
