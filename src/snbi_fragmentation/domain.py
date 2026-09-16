"""Canonical TI-0 vocabulary.

No acquisition, timing, annotation, dataset, or model behavior belongs here.
"""

from enum import StrEnum


class SourceKind(StrEnum):
    VIDEO = "video"
    DOCUMENT = "document"


class StorageKind(StrEnum):
    FILE = "file"
    ZIP_MEMBER = "zip_member"


class Modality(StrEnum):
    XRAY = "xray_radiography"
    RELATIVE_SOLUTE = "relative_solute_field"
    CUMULATIVE_FRAGMENTATION = "cumulative_fragmentation_annotation"
    SCIENTIFIC_DOCUMENT = "scientific_document"
    ACADEMIC_RECORD = "academic_record"


class Condition(StrEnum):
    BOTTOM_UP_ANTI_PARALLEL = "bottom_up_anti_parallel"
    TOP_DOWN_PARALLEL = "top_down_parallel"
    NOT_APPLICABLE = "not_applicable"


EXPECTED_ESM_IDS = frozenset({f"ESM{i}" for i in range(1, 7)})

