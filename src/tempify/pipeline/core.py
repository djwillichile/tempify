"""TempifyPipeline: end-to-end orchestrator (Capa 5).

Sequences the 7 canonical phases and produces a :class:`PipelineResult`.
Per ADR-0014 the class is PascalCase ``TempifyPipeline`` (the module
remains lowercase ``tempify.pipeline``).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import xarray as xr

from tempify.constants import DEFAULT_RM_CONVERGENCE_TOL, DEFAULT_RM_MAX_ITER
from tempify.detection import StructureDetector
from tempify.detection.frequency import (
    TemporalFrequencyResolver,
)
from tempify.interpolation import (
    BaseInterpolator,
    FourierInterpolator,
    LinearInterpolator,
    PchipInterpolator,
    PchipMeanPreservingInterpolator,
    TemporalAxis,
)
from tempify.io import (
    BaseReader,
    BaseWriter,
    GeoTIFFCollectionWriter,
    GeoTIFFReader,
    MultiBandGeoTIFFWriter,
    MultiFileCollectionReader,
    NetCDFReader,
    NetCDFWriter,
    ZarrWriter,
)
from tempify.pipeline.callbacks import PHASES, PipelinePhase, ProgressCallback
from tempify.pipeline.config import PipelineConfig
from tempify.pipeline.errors import (
    PipelineInterpolationError,
    PipelinePreValidationError,
    PipelineReportError,
    PipelineWriteError,
)
from tempify.pipeline.report import ReportGenerator
from tempify.pipeline.result import PipelineResult
from tempify.validation import (
    GeospatialCoherenceValidator,
    MethodVariableCompatibilityChecker,
    PostInterpolationValidator,
    StatisticalReporter,
    ValidationReport,
    VariableProfileMatcher,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger("tempify.pipeline")


class TempifyPipeline:
    """Orchestrate the 7 phases of a tempify run."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self._report_generator = ReportGenerator()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self, source: Path | list[Path]) -> PipelineResult:
        """Execute the pipeline end-to-end."""
        cfg = self.config
        cb = cfg.progress_callback

        # Phase 1: detect
        self._emit(cb, "detect", 0.0, "Detectando estructura y frecuencia")
        detection = StructureDetector().detect(source)
        frequency = TemporalFrequencyResolver(callback=cfg.frequency_resolver_callback).resolve(
            detection.files
        )
        self._emit(cb, "detect", 1.0)

        # Load data via the appropriate reader
        data = self._read(detection.files)

        # Phase 2 + 3: pre-validation (skippable in inspect mode)
        pre_validation = ValidationReport(checks=())
        if not cfg.skip_pre_validation:
            self._emit(cb, "validate_geospatial", 0.0, "Validando coherencia geoespacial")
            geo_report = GeospatialCoherenceValidator().check([data])
            self._emit(cb, "validate_geospatial", 1.0)

            self._emit(
                cb,
                "validate_compatibility",
                0.0,
                "Verificando compatibilidad método/variable",
            )
            profile = self._resolve_profile()
            compat_result = MethodVariableCompatibilityChecker().check(
                cfg.method, profile, force=cfg.force_method
            )
            pre_validation = ValidationReport(checks=(*geo_report.checks, compat_result))
            self._emit(cb, "validate_compatibility", 1.0)
            if not pre_validation.pre_passed:
                raise PipelinePreValidationError(pre_validation)
        else:
            self._emit(cb, "validate_geospatial", 1.0, "(omitida en modo inspect)")
            self._emit(cb, "validate_compatibility", 1.0, "(omitida en modo inspect)")

        # Phase 4: interpolate (skipped in dry_run)
        post_validation: ValidationReport | None = None
        daily_output: xr.DataArray | None = None
        if not cfg.dry_run:
            self._emit(cb, "interpolate", 0.0, f"Interpolando con método '{cfg.method}'")
            daily_output = self._interpolate(data)
            self._emit(cb, "interpolate", 1.0)

            # Phase 5: post-validation
            self._emit(cb, "validate_post", 0.0, "Validando preservación de media y rango")
            profile = self._resolve_profile()
            post_validator = PostInterpolationValidator()
            base_post = post_validator.check(data, daily_output, profile)
            stats = StatisticalReporter().report(daily_output)
            post_validation = ValidationReport(checks=base_post.checks, statistics=stats)
            self._emit(cb, "validate_post", 1.0)

            # Phase 6: write
            self._emit(cb, "write", 0.0, "Escribiendo output a disco")
            outputs = self._write(daily_output)
            self._emit(cb, "write", 1.0)
        else:
            self._emit(cb, "interpolate", 1.0, "(omitida en modo dry_run)")
            self._emit(cb, "validate_post", 1.0, "(omitida en modo dry_run)")
            self._emit(cb, "write", 1.0, "(omitida en modo dry_run)")
            outputs = ()

        # Phase 7: report
        self._emit(cb, "generate_report", 0.0, "Generando reporte de procesamiento")
        try:
            report = self._report_generator.build(
                config=cfg,
                detection=detection,
                frequency=frequency,
                pre_validation=pre_validation,
                post_validation=post_validation,
                outputs=outputs,
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise PipelineReportError(str(exc)) from exc
        self._emit(cb, "generate_report", 1.0)

        return PipelineResult(
            outputs=outputs,
            report=report,
            detection=detection,
            frequency=frequency,
            pre_validation=pre_validation,
            post_validation=post_validation,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _emit(
        self,
        cb: ProgressCallback | None,
        phase: PipelinePhase,
        progress: float,
        message: str | None = None,
    ) -> None:
        logger.info("phase=%s progress=%.2f %s", phase, progress, message or "")
        if cb is None:
            return
        try:
            cb(phase, progress, message)
        except Exception:  # pragma: no cover - never let a UI bug crash the pipeline
            logger.exception("ProgressCallback raised; ignoring.")

    def _read(self, files: tuple[Path, ...]) -> xr.DataArray:
        """Select the appropriate reader for ``files`` and load the data."""
        if len(files) == 1:
            path = files[0]
            reader: BaseReader = (
                NetCDFReader()
                if path.suffix.lower() in {".nc", ".nc4", ".cdf"}
                else GeoTIFFReader()
            )
            data = reader.read(path)
        else:
            data = MultiFileCollectionReader(concat_dim="month").read(list(files))
        # Normalize: ensure "month" is the leading dim with coord 1..12 when
        # we have exactly 12 steps; transpose so interpolators see (month, y, x).
        if "month" in data.dims and data.sizes["month"] == 12:
            if "month" not in data.coords:
                data = data.assign_coords(month=list(range(1, 13)))
            spatial = [d for d in data.dims if d not in ("month",)]
            data = data.transpose("month", *spatial)
        return data

    def _interpolate(self, data: xr.DataArray) -> xr.DataArray:
        """Dispatch to the requested interpolator and run it."""
        method = self.config.method
        interpolator: BaseInterpolator
        if method == "linear":
            interpolator = LinearInterpolator()
        elif method == "pchip":
            interpolator = PchipInterpolator()
        elif method == "pchip_mp":
            opts = self.config.method_options
            interpolator = PchipMeanPreservingInterpolator(
                convergence_tol=float(opts.get("convergence_tol", DEFAULT_RM_CONVERGENCE_TOL)),
                max_iterations=int(opts.get("max_iterations", DEFAULT_RM_MAX_ITER)),
            )
        elif method == "fourier":
            opts = self.config.method_options
            interpolator = FourierInterpolator(n_harmonics=int(opts.get("n_harmonics", 3)))
        else:  # pragma: no cover - exhaustively handled by Literal
            raise PipelineInterpolationError(f"Método desconocido: {method!r}")

        axis = TemporalAxis.from_months(
            year=self.config.target_year, anchor=self.config.monthly_anchor
        )
        try:
            result = interpolator.interpolate(
                data,
                axis,
                cyclic=True,
                chunk_size=self.config.chunk_size,
            )
        except Exception as exc:
            raise PipelineInterpolationError(f"El interpolador '{method}' falló: {exc}") from exc
        return result.compute() if hasattr(result.data, "compute") else result

    def _write(self, data: xr.DataArray) -> tuple[Path, ...]:
        """Dispatch to the writer for the requested output format."""
        fmt = self.config.output_format
        out_dir = Path(self.config.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            writer: BaseWriter
            if fmt == "netcdf":
                writer = NetCDFWriter()
                path = out_dir / "tempify_output.nc"
                return (Path(writer.write(data, path)),)
            if fmt == "multiband_geotiff":
                writer = MultiBandGeoTIFFWriter()
                path = out_dir / "tempify_output.tif"
                return (Path(writer.write(data, path)),)
            if fmt == "geotiff_collection":
                writer = GeoTIFFCollectionWriter()
                files = writer.write(data, out_dir)
                return tuple(Path(p) for p in (files if isinstance(files, list) else [files]))
            if fmt == "zarr":
                writer = ZarrWriter()
                zpath = out_dir / "tempify_output.zarr"
                return (Path(writer.write(data, zpath)),)
        except Exception as exc:
            raise PipelineWriteError(f"Escritura falló: {exc}") from exc
        raise PipelineWriteError(f"Formato de salida desconocido: {fmt!r}")

    def _resolve_profile(self) -> Any:
        matcher = VariableProfileMatcher()
        name = self.config.variable_profile_override or "temperature"
        return matcher.match(name)


# Silence unused-import warnings for PHASES (public re-export from __init__)
_PHASES_EXPORT = PHASES
