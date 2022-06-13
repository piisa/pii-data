# pii-data

This package provides base data structures for the management of PII i.e.
Personally Identifiable Information (it does *not* contain code for processing
documents, or extracting PII from documents).

For the full specification embodied by these base data structures, check the
PIISA Data Specification.

## Data structures

Two main data types are defined: PII Source Documents and PII
Collections. There is also a Source Document data type.


### PII Source Document

A PII Source Document defines the raw data from which PII is detected. This
document is modelled as a sequence of chunks, each one having an identifier
and a raw text content. There could be two variants:
 
 - a *linear* PII Source Document is just a sequence of chunks
 - in a *hierarchical* PII Source document chunks might contain other chunks,
   in a nested fashion
   
The Python data structure for a chunk is just a Python dictionary; a PII
Source Document could be a nested dictionary, a list of dictionaries or a
combination of both.

The official dump representation of a PII Source Document is in the form of a
YAML file.


### PII Collection

A PII Collection contains a list of detected/extracted PII Entities. Each
entity contains all the information needed to correctly identify one PII
instance and locate it in the document it belongs to.

These are the data classes defined:
 * `PiiCollection`: the full collection of PII
 * `PiiEntity`: one PII instance
 * `PiiDetector`: an objecto to describe the module used to generate a given
    `PiiEntity` object
	
`PiiCollection` objects have a `dump()` method that allows writing them in a
standard format, with two representations:
 * a JSON representation, adequate for storage
 * a NDJSON representation (newline-delimited JSON), intended for processing
   and streaming


### Source document

A simple representation of document data as a list of text chunks. It allows
to define a hierarchy between chunks.


## Online behaviour

There is partial support to use these data classes in an [streaming] fashion,
proving a way to feed data incrementally.



[streaming]: doc/stream.md
