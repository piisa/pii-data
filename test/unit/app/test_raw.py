from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest

from pii_data.helper import load_yaml
import pii_data.doc.rawtext as doc
import pii_data.app.rawdoc as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(doc, 'uuid', mock_uuid)



def test10_read(fix_uuid):
    """Test reading a raw file"""

    with tempfile.NamedTemporaryFile() as f:
        f.close()

        mod.from_raw(fname('doc-example.txt'), f.name, indent=2)
        #mod.from_raw(fname('doc-example.txt'), fname('doc-example-2.yaml'), 2)
        got = load_yaml(f.name)

        exp = load_yaml(fname('doc-example-tree-id.yaml'))
        assert got == exp


def test20_write():
    """Test writing a raw file"""

    with tempfile.NamedTemporaryFile() as f:
        f.close()

        mod.to_raw(fname('doc-example-tree.yaml'), f.name, indent=2)
        #mod.from_raw(fname('doc-example.txt'), fname('doc-example-2.yaml'), 2)
        got = readfile(f.name)

        exp = readfile(fname('doc-example.txt'))
        assert got == exp
