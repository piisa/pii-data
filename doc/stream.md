# Stream processing

In order to be able to process potentially huge documents, the data structures
should allow stream processing. Currently this is the status:

## Source documents

The standard `SrcDocument` abstract base class will happily iterate in a
streaming fashion if the child class provides a `get_chunks()` method that
yields chunks in iteration.

So in order to provide stream processing capabilities:
 * subclass the `SrcDocument` into an e.g. `StreamingSrcDocument`
 * implement a `get_chunks()` method in the subclass, which must return
   an iterator producing chunks (a chunk must be either a dict containing a
   `data` member, or just the chunk payload)
   
This should be enough to let the tools process the document incrementally.

The `LocalSrcDocument` subclass and variants can only process full local
documents, since it either loads them from file, or accepts the full set of
document chunks in the constructor or the `set_chunks()` method.



## PiiCollections

Currently the PiiCollection format does not allow a fully streamable operation;
the PII instances need to be fully computed before the data can be dumped. This
is mostly because there is a data header that contains the list of PII
Detectors, and it gets built as new PII instances are added.

Nevertheless the data _can_ be dumped incrementally into an output file-like
object, if the NDJSON format is chosen.

_A future version will be made fully streamable by **preloading** all
detectors that might get used, so that the header can be dumped immediately_

