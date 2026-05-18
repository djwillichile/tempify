"""Tests del módulo tempify.datasets (v0.1.5)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import xarray as xr


class TestCreateWorldclimLikeSample:
    """create_worldclim_like_sample() — genera 12 GeoTIFFs sintéticos."""

    def test_genera_12_archivos_tif(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample

        result = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        tif_files = list(result.glob("*.tif"))
        assert len(tif_files) == 12

    def test_nombres_siguen_convencion_worldclim(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        esperados = {f"wc2.1_2.5m_tavg_{m:02d}.tif" for m in range(1, 13)}
        actuales = {f.name for f in out.glob("*.tif")}
        assert esperados == actuales

    def test_forma_del_raster(self, tmp_path: Path) -> None:
        import rioxarray  # noqa: F401

        from tempify.datasets import create_worldclim_like_sample

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        da = xr.open_dataarray(
            out / "wc2.1_2.5m_tavg_01.tif", engine="rasterio"
        ).squeeze("band", drop=True)
        assert da.shape == (8, 8)

    def test_crs_es_epsg4326(self, tmp_path: Path) -> None:
        import rioxarray  # noqa: F401

        from tempify.datasets import create_worldclim_like_sample

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        da = xr.open_dataarray(out / "wc2.1_2.5m_tavg_06.tif", engine="rasterio")
        assert da.rio.crs.to_epsg() == 4326

    def test_reproducibilidad_con_misma_semilla(self, tmp_path: Path) -> None:
        import rioxarray  # noqa: F401

        from tempify.datasets import create_worldclim_like_sample

        out1 = create_worldclim_like_sample(tmp_path / "a", n_pixels=8, seed=42, overwrite=True)
        out2 = create_worldclim_like_sample(tmp_path / "b", n_pixels=8, seed=42, overwrite=True)
        da1 = xr.open_dataarray(out1 / "wc2.1_2.5m_tavg_07.tif", engine="rasterio")
        da2 = xr.open_dataarray(out2 / "wc2.1_2.5m_tavg_07.tif", engine="rasterio")
        np.testing.assert_array_equal(da1.values, da2.values)

    def test_semillas_distintas_producen_output_distinto(self, tmp_path: Path) -> None:
        import rioxarray  # noqa: F401

        from tempify.datasets import create_worldclim_like_sample

        out1 = create_worldclim_like_sample(tmp_path / "a", n_pixels=8, seed=42, overwrite=True)
        out2 = create_worldclim_like_sample(tmp_path / "b", n_pixels=8, seed=99, overwrite=True)
        da1 = xr.open_dataarray(out1 / "wc2.1_2.5m_tavg_01.tif", engine="rasterio")
        da2 = xr.open_dataarray(out2 / "wc2.1_2.5m_tavg_01.tif", engine="rasterio")
        assert not np.array_equal(da1.values, da2.values)

    def test_retorna_directorio_de_salida(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample

        out_dir = tmp_path / "sample"
        result = create_worldclim_like_sample(out_dir, n_pixels=8, overwrite=True)
        assert result == out_dir

    def test_overwrite_false_omite_generacion_si_existen_archivos(
        self, tmp_path: Path
    ) -> None:
        from tempify.datasets import create_worldclim_like_sample

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        primer_archivo = out / "wc2.1_2.5m_tavg_01.tif"
        mtime_antes = primer_archivo.stat().st_mtime

        create_worldclim_like_sample(out, n_pixels=8, overwrite=False)
        assert primer_archivo.stat().st_mtime == mtime_antes

    def test_monthly_values_invalido_lanza_value_error(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample

        with pytest.raises(ValueError, match="12 elementos"):
            create_worldclim_like_sample(
                tmp_path / "out", monthly_values=(1.0, 2.0), overwrite=True
            )

    def test_nombre_de_variable_personalizado(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample

        out = create_worldclim_like_sample(
            tmp_path / "out", variable="prec", n_pixels=8, overwrite=True
        )
        assert (out / "wc2.1_2.5m_prec_01.tif").exists()
        assert not (out / "wc2.1_2.5m_tavg_01.tif").exists()


class TestReadMonthlyStack:
    """read_monthly_stack() — carga 12 GeoTIFFs como DataArray (month, y, x)."""

    def test_retorna_dataarray(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample, read_monthly_stack

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        stack = read_monthly_stack(out)
        assert isinstance(stack, xr.DataArray)

    def test_forma_es_12_y_x(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample, read_monthly_stack

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        stack = read_monthly_stack(out)
        assert stack.dims == ("month", "y", "x")
        assert stack.sizes["month"] == 12
        assert stack.sizes["y"] == 8
        assert stack.sizes["x"] == 8

    def test_coordenada_month_es_1_a_12(self, tmp_path: Path) -> None:
        from tempify.datasets import create_worldclim_like_sample, read_monthly_stack

        out = create_worldclim_like_sample(tmp_path / "out", n_pixels=8, overwrite=True)
        stack = read_monthly_stack(out)
        assert list(stack["month"].values) == list(range(1, 13))
