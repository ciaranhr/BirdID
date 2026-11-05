"""tools/stamp_version.py: CI stamps sw.js with the commit hash before every deploy."""
import os

import pytest

import stamp_version as sv
from paths import APP


def test_stamps_the_real_sw_js():
    with open(os.path.join(APP, "sw.js")) as f:
        text = f.read()
    out = sv.stamp(text, "abc1234")
    assert "const VERSION = 'abc1234';" in out
    assert out.count("\n") == text.count("\n")  # nothing else touched
    assert sv.stamp(out, "def5678").count("def5678") == 1  # idempotent shape


def test_missing_or_duplicate_line_fails_loudly():
    with pytest.raises(ValueError, match="found 0"):
        sv.stamp("const VERSIONS = 'x';\n", "abc")
    with pytest.raises(ValueError, match="found 2"):
        sv.stamp("const VERSION = 'a';\nconst VERSION = 'b';\n", "abc")


@pytest.mark.parametrize("bad", ["", "a'b", "a b", "x;alert(1)"])
def test_rejects_unsafe_versions(bad):
    with pytest.raises(ValueError):
        sv.stamp("const VERSION = 'dev';\n", bad)


def test_cli_writes_file(tmp_path):
    p = tmp_path / "sw.js"
    p.write_text("const VERSION = 'dev'; // comment\nconst SHELL = `shell-${VERSION}`;\n")
    sv.main(["stamp_version.py", "9acf0ac", str(p)])
    assert p.read_text() == "const VERSION = '9acf0ac'; // comment\nconst SHELL = `shell-${VERSION}`;\n"
