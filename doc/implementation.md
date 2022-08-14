# Implementing SrcDocument subclasses

The `SrcDocument` and direct child classes (sequence, tree, table) are
abstract subclasses: they provide the base infrastructure to operate with
documents:
 * base constructors
 * iterators: 
     - the `iter_full()` method: a _full_ chunk iterator (the object default
	   iterator is an alias to this method). This method generates
	   `DocumentChunk` objects.
	 - the `iter_struct()` method: a _native_ structured iterator, whose
	   output shows more of the document structure. This method produces
	   a Python dictionary for each chunk:
	     - for Sequence documents, this iterator produces the same results as
		   for the _full_ iterator (but each chunk is a dict instead of a
		   `DocumentChunk`)
	     - for Tree documents it yields document subtrees, which represent
		   top-level sections of the document
		 - for Table documents it yields full document rows
		 
However, as mentioned, those classes are abstract: they lack the concrete
procedure to generate data from the source to feed those iterators. In order
to create a fully functioning class, it is necessary:
 1. To inherit from the proper base class (depending on the data native
    structure): `SequenceSrcDocument`, `TreeSrcDocument`,
    `TableSrcDocument`
 2. To implement the low-level `iter_base()` method, used by the high-level
    iterators
   
## iter_base

This method must return an iterator that will produce data according to the
_native_ data structure. In general the method can deliver, for each iteration: 
 - either a dictionary, containing at least a `data` field (which has the 
   chunk payload)
 - or an arbitrary object (e.g. a plain string) representing the payload
   directly. It will then be wrapped around to produce the dictionary
   
Depending on the document type, there are particularities:
 - Sequence documents must produce a linear sequence of chunks, in either of
   the two formats mentiones above
 - Table document must produce document rows, in also either of the two
   formats: in this case either a list directly containing the row, or a 
   dictionary with a `data` field containing the row as a list
 - Tree documents must produce elements representing document subtrees. 
   Each such element is either:
     - a top-level isolated paragraph, as either a dict or a plain string
	 - a dict containing a top-level section of the document with
       all its subsections and paragraphs recursively included, following the
	   document hierarchy (note that in this case the dict format is compulsory)


### Chunk identifiers

Each delivered element needs an identifier (unique across the document). This
is provided as:
 * if the element is a dict, and contains an `id` field, it is used
 * if it does not contain it, or it is not a dict, an identifier is generated
   by the parent class. The structure of such identifier depends on the document
   type, and in general it should be considered as an opaque string

Note that the two top-level iterators, `iter_full()` and `iter_struct()`, 
will chunk information in different ways (with the exception of the Sequence
documents) and will produce _different_ identifiers.


## _local_ classes

A variant of the `SrcDocumet` is the `LocalSrcDocument` class (and
associated subclasses; there is one for each of the base classes.

The additional functionality provided by this _extra_ base classes is:

* the capability to explicitly set the list of chunks for the document, either
  in the constructor or in an additional `set_chunks()` method
* dump the document to a local YAML file

Finally, there is an additional `load_file()` dispatcher function that can
_load_ a YAML file (in the format created by the dump functionality) and
re-create the appropriate `LocalSrcDocument`  subclass.


### Subclassing the local classes

If a subclass is done from one of the local classes instead of a base class,
then the object gains the set/dump functionality of the local class. Other
than that, the mechanics are the same.
