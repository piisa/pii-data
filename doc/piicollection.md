# PiiCollection

A `PiiCollection` class is a container class. It contains inside a list of
PiiEntity objects, added to it via its `add()' method. When iterated, it
produces such list.

The object also contains a header that keeps general information. Among this
information is a list of the PII detectors that have been used to extract the
PII instances stored into it. Those detectors have the form of `PiiDetector`
objects, and they are added with entity objects: each `PiiEntity` object added
via `add()` can also add its corresponding `PiiDetector` (the class ensures
that there is always only one copy for each detector).


# PiiCollectionLoader

This is a subclass of `PiiCollection`, which adds `load()` method to be able
to recover PII information from an exported file (see below)


## Export/import

`PiiCollection` objects have a `dump()` method that allows writing them in a
standard format, with two representations:
 * a JSON representation, adequate for storage
 * a NDJSON representation (newline-delimited JSON), intended for processing
   and streaming

These serializations can then be read back with the `PiiCollectionLoader`
subclass.
