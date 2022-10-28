# pii-data

This package provides base data structures for the management of PII i.e.
Personally Identifiable Information (it does *not* contain code for processing
documents, or extracting PII from documents).

For the full specification embodied by these base data structures, check the
[PIISA Data Specification].

## Data structures

Two main data types are defined to hold PII information: PII Entities and PII
Collections. There is also a Source Document data type.


### PII Source Document

A PII Source Document defines the raw data from which PII is detected. This
document is modeled as a number of chunks, each one having an identifier and a 
data contents (a raw text excerpt, or other types of content). This is managed
in this package by the [SrcDocument] class and subclasses.

The package contains the capability to dump a Source Document to a local file,
following a standardized schema, and to read it back from the file. This schema
uses YAML as support file format, and is the _only_ document read capability
natively provided by the package (to read other formats into Source Document
objects there is an auxiliary [pii-preprocess] package, or you can [implement
yout own]).

The package can also export documents as raw text files.


### PII Collection

A PII Collection contains a list of detected/extracted PII Entities. Each
entity contains all the information needed to correctly identify one PII
instance and locate it in the document it belongs to.

These are the PII data classes defined:
 * [PiiEntity]: one PII instance
 * [PiiCollection]: the full collection of PII (the additional
   `PiiCollectionLoader` subclass can load a collection from a JSON file)
 * `PiiDetector`: an object to describe the module used to generate a given
   `PiiEntity` object


## Online behaviour

There is partial support to use these data classes in an [streaming] fashion,
providing a way to feed data incrementally.


[implement your own]: doc/implementing-srcdocument.md
[streaming]: doc/stream.md
[SrcDocument]: doc/srcdocument.md
[PiiEntity]: doc/piientity.md
[PiiCollection]: doc/piicollection.md
[PIISA Data Specification]: https://github.com/piisa/piisa/
[pii-preprocess]: https://github.com/piisa/pii-preprocess/
