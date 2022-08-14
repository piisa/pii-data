# Source Document

A PII Source Document defines the raw data from which PII is detected. 
A Source Document, as described in the [data specification], contains two
elements:
 * a document header, containing global metadata
 * a number of *document chunks*, containing the document payload.

The Python data structure for a document chunk is `DocumentChunk`, which
is just a Python `namedtuple`, with up to three elements:
 * `id`: chunk identifier
 * `data`: the chunk contents (typically a raw unicode text blob).
 * `context`: contextual information associated to the chunk (optional)


## Document types

Three document variants are defined:
 
 - a *sequence* PII Source Document is just a sequence of chunks
 - in a *tree* PII Source Document chunks might contain other chunks,
   in a nested fashion
 - a *table* PII Source Document has a table structure (rows and columns).
   

## Root classes

The base Python class to manage a source document is the `SrcDocument` class.
This is an abstract class; to be usable a child class needs to [implement] the
`iter_base()` method, which yields an iterator over document base chunks
(producing chunk payloads).

There are three subclasses of `SrcDocument`, for each of the three types of
documents:
 * `SequenceSrcDocument`
 * `TreeSrcDocument`
 * `TableSrcDocument`

These are still abstract classes, so they still need the implementation of
the `iter_base()` method.


## Local document classes

One additional defined subclass of a `SrcDocument` is the 
`BaseLocalSrcDocument` class, which holds all document chunks in memory (the
original `SrcDocument` class might produce them on demand from a source), 
and can load/dump to a file.

Subclasses of `BaseLocalSrcDocument` are also defined for each of the three
document types:
 * `SequenceLocalSrcDocument`
 * `TreeLocalSrcDocument`
 * `TableLocalSrcDocument`

Finally, the `LocalSrcDocument` is a dispatcher class that can open and read
any of those three classes of local source documents and return an object of
the right class (after parsing the document header).


## File format

The official dump representation of a PII Source Document is in the form of a
YAML file. The package generates it using the [block literal style], to ease
human reading.

However any valid YAML file will do for reading the file back. And a JSON
representation would also be read by the package (since JSON is a subset
of YAML anyway).


[data specification]: https://github.com/piisa/piisa/
[block literal style]: https://yaml.org/spec/1.2.2/#812-literal-style
[implement]: implementation.md
