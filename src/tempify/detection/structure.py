"""Structure detector for tempify inputs.

Classifies an input as one of:

- ``StructureMode.SINGLE_STACK`` (mode A): one multi-band file, or one
  NetCDF with a temporal dim.
- ``StructureMode.MONOLAYER_COLLECTION`` (mode B): a folder containing
  multiple single-band files, sorted in NFC-deterministic order.
- ``StructureMode.EXPLICIT_LIST`` (mode C): the caller provided an
  explicit list of paths; structure detection is bypassed but
  homogeneity is still required.

Returns a :class:`StructureDetectionResult` with the subset of the
canonical :class:`DetectionConfidence` keys this layer can compute,
per ADR-0008 ("Composición por capas").
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Final, TypedDict

import rasterio  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class StructureDetectionError(Exception):
    """Base class for structure detection errors."""

    code: ClassVar[str] = "TEMPIFY-DET-000"


class EmptyInputError(StructureDetectionError):
    """Raised when the input list or folder contains no readable raster."""

    code: ClassVar[str] = "TEMPIFY-DET-001"

    def __init__(self, source: Path | list[Path]) -> None:
        super().__init__(f"La entrada está vacía o no contiene rásters reconocibles: {source!r}.")


class AmbiguousStructureError(StructureDetectionError):
    """Raised when the structure cannot be determined and no callback is provided."""

    code: ClassVar[str] = "TEMPIFY-DET-002"

    def __init__(self, candidates: tuple[StructureMode, ...]) -> None:
        self.candidates = candidates
        super().__init__(
            f"No se pudo determinar la estructura de la entrada de forma "
            f"unívoca. Modos candidatos: {[c.value for c in candidates]}. "
            "Provea un callback de desambiguación o invoque modo C con una "
            "lista explícita."
        )


class HeterogeneousFilesError(StructureDetectionError):
    """Raised when the collection has incompatible files (e.g., mixed CRS)."""

    code: ClassVar[str] = "TEMPIFY-DET-003"

    def __init__(self, reason: str) -> None:
        super().__init__(
            f"Los archivos de la colección no son homogéneos: {reason}. "
            "Use --force para procesar con la mejor aproximación, o armonice "
            "los archivos antes de invocar tempify."
        )


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class StructureMode(StrEnum):
    """Detected input structure (per ADR-0008)."""

    SINGLE_STACK = "A"
    MONOLAYER_COLLECTION = "B"
    EXPLICIT_LIST = "C"


class StructureConfidencePartial(TypedDict):
    """Subset of DetectionConfidence computed by this layer (ADR-0008)."""

    structure_mode: float
    homogeneity: float


@dataclass(frozen=True, slots=True)
class StructureDetectionResult:
    """Outcome of :meth:`StructureDetector.detect`.

    Attributes
    ----------
    structure_mode : StructureMode
        Classified mode A/B/C.
    files : tuple[Path, ...]
        Ordered list of files that compose the input (NFC-sorted).
    confidence : StructureConfidencePartial
        Per-key confidence in [0.0, 1.0]. The Pipeline (Capa 5) merges
        this with the other contributors to form the full canonical
        ``DetectionConfidence`` per ADR-0008.
    band_descriptions : tuple[str, ...] | None
        Band-level metadata (e.g., dates) extracted from mode-A
        multi-band GeoTIFFs. ``None`` when not applicable.
    """

    structure_mode: StructureMode
    files: tuple[Path, ...]
    confidence: StructureConfidencePartial
    band_descriptions: tuple[str, ...] | None = field(default=None)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


SIDECAR_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {
        ".aux.xml",
        ".ovr",
        ".tfw",
        ".prj",
        ".cpg",
        ".lock",
        ".provenance.json",
    }
)
"""Auxiliary files that should be skipped when scanning a directory."""

RASTER_EXTENSIONS: Final[frozenset[str]] = frozenset({".tif", ".tiff", ".nc", ".nc4", ".cdf"})


def _nfc(p: Path) -> str:
    return unicodedata.normalize("NFC", str(p))


def _is_sidecar(p: Path) -> bool:
    name = p.name.lower()
    return any(name.endswith(ext) for ext in SIDECAR_EXTENSIONS)


def _is_raster(p: Path) -> bool:
    return p.suffix.lower() in RASTER_EXTENSIONS


def _list_dir(dir_path: Path, recurse: bool = False) -> list[Path]:
    iterator = dir_path.rglob("*") if recurse else dir_path.iterdir()
    return [p for p in iterator if p.is_file() and not _is_sidecar(p)]


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class StructureDetector:
    """Classify the input as mode A / B / C and return ordered files."""

    def __init__(
        self,
        disambiguation_callback: Callable[[tuple[StructureMode, ...]], StructureMode] | None = None,
        recurse: bool = False,
    ) -> None:
        self.disambiguation_callback = disambiguation_callback
        self.recurse = recurse

    def detect(self, source: Path | list[Path]) -> StructureDetectionResult:
        """Classify ``source`` into mode A / B / C and return the result."""
        if isinstance(source, list):
            return self._detect_explicit_list(source)
        path = Path(source)
        if path.is_dir():
            return self._detect_directory(path)
        if path.is_file():
            return self._detect_single_file(path)
        raise EmptyInputError(source)

    # ------------------------------------------------------------------
    # Mode C
    # ------------------------------------------------------------------
    def _detect_explicit_list(self, source: list[Path]) -> StructureDetectionResult:
        files = [Path(p) for p in source if Path(p).is_file() and _is_raster(Path(p))]
        if not files:
            raise EmptyInputError(source)
        ordered = tuple(sorted(files, key=_nfc))
        # Mode C is asserted by the caller; trust them but verify homogeneity downstream.
        return StructureDetectionResult(
            structure_mode=StructureMode.EXPLICIT_LIST,
            files=ordered,
            confidence={"structure_mode": 1.0, "homogeneity": 1.0},
        )

    # ------------------------------------------------------------------
    # Mode A
    # ------------------------------------------------------------------
    def _detect_single_file(self, path: Path) -> StructureDetectionResult:
        if not _is_raster(path):
            raise EmptyInputError(path)
        bands_desc = self._read_band_descriptions(path)
        n_bands = self._count_bands(path)
        # Mode A confidence is 1.0 when a single file is given.
        return StructureDetectionResult(
            structure_mode=StructureMode.SINGLE_STACK,
            files=(path,),
            confidence={"structure_mode": 1.0, "homogeneity": 1.0},
            band_descriptions=bands_desc if n_bands > 1 else None,
        )

    @staticmethod
    def _count_bands(path: Path) -> int:
        if path.suffix.lower() in {".tif", ".tiff"}:
            try:
                with rasterio.open(path) as src:
                    return int(src.count)
            except rasterio.errors.RasterioIOError:
                return 1
        return 1

    @staticmethod
    def _read_band_descriptions(path: Path) -> tuple[str, ...] | None:
        if path.suffix.lower() not in {".tif", ".tiff"}:
            return None
        try:
            with rasterio.open(path) as src:
                descs = src.descriptions
        except rasterio.errors.RasterioIOError:
            return None
        if not descs or all(d is None or d == "" for d in descs):
            return None
        return tuple(d if d is not None else "" for d in descs)

    # ------------------------------------------------------------------
    # Mode B
    # ------------------------------------------------------------------
    def _detect_directory(self, dir_path: Path) -> StructureDetectionResult:
        candidates = [p for p in _list_dir(dir_path, recurse=self.recurse) if _is_raster(p)]
        if not candidates:
            raise EmptyInputError(dir_path)
        ordered = tuple(sorted(candidates, key=_nfc))
        # Degenerate case: a single file in a directory.
        if len(ordered) == 1:
            return StructureDetectionResult(
                structure_mode=StructureMode.SINGLE_STACK,
                files=ordered,
                confidence={"structure_mode": 0.85, "homogeneity": 1.0},
                band_descriptions=self._read_band_descriptions(ordered[0]),
            )
        # Compute homogeneity confidence by checking file formats.
        suffixes = {p.suffix.lower() for p in ordered}
        homo = 1.0 if len(suffixes) == 1 else 0.5
        if len(suffixes) > 1 and self.disambiguation_callback is None:
            raise HeterogeneousFilesError(f"extensiones mixtas: {sorted(suffixes)}")
        return StructureDetectionResult(
            structure_mode=StructureMode.MONOLAYER_COLLECTION,
            files=ordered,
            confidence={"structure_mode": 0.95, "homogeneity": homo},
        )


__all__ = [
    "SIDECAR_EXTENSIONS",
    "AmbiguousStructureError",
    "EmptyInputError",
    "HeterogeneousFilesError",
    "StructureConfidencePartial",
    "StructureDetectionError",
    "StructureDetectionResult",
    "StructureDetector",
    "StructureMode",
]
