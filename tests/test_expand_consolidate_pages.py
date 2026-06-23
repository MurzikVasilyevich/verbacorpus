import pytest
from expand.consolidate_pages import apply_corrections


def test_apply_corrections_replaces_and_preserves_order():
    proverbs = [
        {"rid": "r0", "ref": "025", "text": "Іржа їсть залізо"},
        {"rid": "r1", "ref": "025", "text": "Горе ззазавить"},
    ]
    out = apply_corrections(proverbs, {"r1": "Горе задавить"})
    assert out == [
        {"ref": "025", "text": "Іржа їсть залізо"},
        {"ref": "025", "text": "Горе задавить"},
    ]


def test_unknown_correction_rid_raises():
    proverbs = [{"rid": "r0", "ref": "1", "text": "x"}]
    with pytest.raises(ValueError):
        apply_corrections(proverbs, {"rZ": "y"})
