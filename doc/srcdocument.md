# Source Document

A PII Source Document defines the raw data from which PII is detected. 
A Source Document, as described in the [data specification], contains two
elements:
 * a document header, containing global metadata
 * a number of *document chunks*, containing the document payload. The Python
   data structure to manage a document chunk is [DocumentChunk]


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

Local documents have two means of acquiring their chunks:
 * all in one step, via the `set_chunks()` method (or the equivalent parameter
   in the constructor)
 * incrementally, one at a time, via the `add_chunk()` method. In this case,
   for documents with structure (tree, table), fields in the chunk context are
   used to determine the chunk position within that structure.

## Dispatcher classes

Two wrapper classes can be used to abstract away the document variant:
 * `LocalSrcDocument` is a dispatcher class that takes as its first argument
   the document variant (`sequence`, `tree`, `table`) and creates a
   `*LocalSrcDocument` of the appropriate class
 * `LocalSrcDocumentFile` is a dispatcher class that takes as its first
   argument a filename contianing a serialized document (see below), opens
   and loads it and returns an object of the right class (after parsing the
   document header).

The `LocalSrcDocumentFile` class is only a thin wrapper around the
`load_file()` dispatcher function, to make it a class object.


## File format

The official dump representation of a PII Source Document is in the form of a
YAML file.

The package generates it using the [block literal style], to ease human reading.
However any valid YAML file will do for reading the file back. And a JSON
representation would also be read by the package (since JSON is a subset
of YAML anyway).


[data specification]: https://github.com/piisa/piisa/
[block literal style]: https://yaml.org/spec/1.2.2/#812-literal-style
[implement]: implementing-srcdocument.md
[DocumentChunk]: chunks.md
