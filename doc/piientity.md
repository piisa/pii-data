# PiiEntity

A PiiEntity object contains an instance of a PII element detected in a
document.

## Attributes

An instantiated PiiEntity object has three attributes:
 * `info`: a `PiiEntityInfo` instance that informs about base features
   of the entity (entity type, subtype, language, country)
 * `fields`: a dictionary describing the values for this PII instance
 * `pos`: an integer indicating the character-based position of the PII in
   the document chunk it was detected in

### PiiEntityInfo

This is an object with these fields:
 * `pii`: the main PII Type, as a `PiiEnum` value
 * `subtype`: a string denoting a more concrete characterization of the PII
   (i.e. a subdivision of the main PII type)
 * `lang`: the language this PII instance refers to
 * `country`: the country this PII instance relates to, if applicable


### Dictionary of fields

The `fields` dictionary, as mentioned, is one of the object attributes.
It always contains:
 * `type`: a string describing the PII main type [*]
 * `value`: the string with the PII expression in the document
 * `chunkid`: the id of the document chunk it was found in
 
And it can also contain the following optional fields:
 * `docid`: an identifier for the document the PII belongs to
 * `detector`: the index of the detector that generated the PII
 * `process`: information about the processing stage (if it exists, this is
   itself a dictionary, with fields like `stage` or `action` informing about
   the current stage, plus a `history` field holding information about
   previous stages)
 * `extra`: a field holding an additional dictionary to store arbitrary
   properties

Note that the PiiEntity object contains no information about the end span of
the entity value. Instead, this can be computed by adding the _length_ of the
entity (the `len()` function can be applied to the object) to the `pos`
attribute.


## Export/import

PiiEntity objects provide a `asdict()` method that returns the descriptors of
the object as a Python dictionary.

The dictionary contains all the elements in the `fields` and `info`
attributes, plus `start` and `end` elements (computed from the `pos`
attribute and the entity length) that give the entity position in the document
chunk.

There is also a class method `PiiEntity.fromdict()` that takes such a
dictionary and recreates and returns the object.

 
[*] Note that given an `obj` object of class `PiiEntity`:
 - `obj.info.pii` is a `PiiEnum` object
 - `obj.fields["type"]` is a string

Both elements contain the same information, since it always holds that
`obj.fields["type"] == obj.info.pii.name`
