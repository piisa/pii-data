"""
Test the DocumentChunk and associated classes
"""

import pii_data.types.doc.chunker as mod


# ----------------------------------------------------------------

def test100_chunk():
    """Test object creation"""
    obj = mod.DocumentChunk(1, "an example")
    assert obj.id == "1"
    assert obj.data == "an example"
    assert obj.context is None

def test110_chunk_context():
    """Test object creation, with context"""
    obj = mod.DocumentChunk(1, "an example", {"before": 4})
    assert obj.id == "1"
    assert obj.data == "an example"
    assert obj.context == {"before": 4}


def test120_chunk_eq():
    """Test chunk equality"""
    elem = {"data": "an example"}
    obj1 = mod.DocumentChunk(1, elem["data"])
    obj2 = mod.DocumentChunk(1, elem["data"])
    obj3 = mod.DocumentChunk(2, elem["data"])
    obj4 = mod.DocumentChunk(1, elem["data"], {"before": 12})

    assert obj1 == obj2
    assert obj1 != obj3
    assert obj1 != obj4


def test120_chunk_dict():
    """Test chunk asdict"""
    obj1 = mod.DocumentChunk(1, "an example")
    obj2 = mod.DocumentChunk(1, "an example", {"after": 44})

    assert {"id": '1', "data": "an example"} == obj1.asdict()
    assert {"id": '1', "data": "an example", "context": {"after": 44}} == obj2.asdict()


# ----------------------------------------------------------------

def test200_generator():
    """Test constructor"""
    mod.ChunkGenerator()


def test210_generator_call():
    """Test constructor"""
    cg = mod.ChunkGenerator()
    elem = {"data": "an example"}
    chunk = cg(elem)
    assert chunk.id == "1"
    assert chunk.data == "an example"


def test220_generator_call_context():
    """Test constructor"""
    cg = mod.ChunkGenerator()
    elem = {"data": "an example"}
    chunk = cg(elem, {"before": "previous"})
    assert chunk.id == "1"
    assert chunk.data == "an example"
    assert chunk.context == {"before": "previous"}
