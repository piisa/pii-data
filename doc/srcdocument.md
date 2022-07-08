# Source Document

A PII Source Document defines the raw data from which PII is detected. 
A Source Document, as described in the [data specification], contains two
elements:
 * a document header, containing global metadata
 * a number of *document chunks*, containing the document payload.

The Python data structure for a document chunk is `DocumentChunk`, which
is just a Python `namedtuple`, with up to three elements:
 * `id`: chunk identifier
 * `data`: the chunk contents (a raw text excerpt, or other types of content).
 * `context`: contextual information associated to the chunk (optional)


## Document types

Three document variants are defined:
 
 - a *sequential* PII Source Document is just a sequence of chunks
 - in a *tree* PII Source Document chunks might contain other chunks,
   in a nested fashion
 - a *tabular* PII Source Document has a table structure (rows and columns).
   

## Base classes

The base Python class to manage a source document is the `SrcDocument` class.
This is an abstract class; to be usable a child class needs to implement the 
`get_chunks()` method, which yields an iterator over the document chunks
(producing chunk payloads).

There are three subclasses of `SrcDocument`, for each of the three types of
documents:
 * `SequentialSrcDocument`
 * `TreeSrcDocument`
 * `TabularSrcDocument`

These are still abstract classes, so they still need a subclass implementing
the `get_chunks()` method (or, in the case of the `TreeSrcDocument`, a
`top_chunks()` method).


## Local document classes

One full instance of a `SrcDocument` is the `LocalSrcDocument` class, which
can hold all document chunks in memory, and can load/dump to a file. 

Subclasses of `LocalSrcDocument` are also defined for each of the three
document types:
 * `SequentialLocalSrcDocument`
 * `TreeLocalSrcDocument`
 * `TabularLocalSrcDocument`


## File format

The official dump representation of a PII Source Document is in the form of a
YAML file, typically using the [block literal style], to ease human reading.

However a JSON representation would also be processed by the package (since
JSON is a subset of YAML anyway).



[data specification]: https://github.com/piisa/piisa/
[block literal style]: https://yaml.org/spec/1.2.2/#812-literal-style
