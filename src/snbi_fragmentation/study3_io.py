"""Receipt-bound Study3 admission delegating directed reads to Study2-D.

Import and construction are inert. No decoder, mmap, bulk container read or
alternative path resolver exists here. The caller must authenticate the fixed
TRAIN manifest before creating this capability.
"""
from copy import deepcopy
import hashlib
import json

from .study2d_io import TrainAccessError, TrainCorpusAccess, validate_rows, is_hex


class Study3AccessError(TrainAccessError):
    """Admission failure consumes the Study3 access capability."""


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


class TrainReceiptGrant:
    """Single immutable membership grant; identities are checked before paths."""

    def __init__(self, rows, receipt_sha256, method_freeze_sha):
        validate_rows(rows)
        if not is_hex(receipt_sha256, 64) or not is_hex(method_freeze_sha, 40):
            raise Study3AccessError("durable receipt and method freeze required")
        self._rows = deepcopy(rows)
        self._membership_hash = canonical_hash(rows)
        self._receipt = receipt_sha256
        self._freeze = method_freeze_sha
        self._used = False

    def __call__(self, action, rows):
        if self._used:
            raise Study3AccessError("TRAIN grant already consumed")
        self._used = True
        # Every invocation, including a bad invocation, consumes this object.
        if action != "LOAD_TRAIN_ROWS":
            raise Study3AccessError("unknown TRAIN action")
        validate_rows(rows)
        if canonical_hash(rows) != self._membership_hash:
            raise Study3AccessError("TRAIN identities, types or locators changed")
        return {"authorized": True, "execution_receipt_sha256": self._receipt,
                "method_freeze_sha": self._freeze}


class Study3TrainAccess:
    """No independent experimental reader: retain historical I/O guarantees."""

    def __init__(self, root, rows, grant=None, audit=None):
        self._reader = TrainCorpusAccess(root, rows, grant=grant, audit=audit)

    @property
    def audit(self):
        return self._reader.audit

    def load(self):
        return self._reader.load()

    def close(self):
        self._reader.close()
