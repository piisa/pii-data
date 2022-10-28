# PiiEntity

A PiiEntity object contains an instance of a PII element detected in a
document.

## Attributes

An instantiated PiiEntity object has three attributes:
 * `type`: a `PiiEnum` instance that informs the main type of entity
 * `fields`: a dictionary describing the PII
 * `pos`: an integer indicating the character-based position of the PII in
   the document chunk it was detected in


## Dictionary of fields

The `fields` dictionary, as mention, is one of the object attributes.
It always contains:
 * `type`: a string describing the PII main type [*]
 * `value`: the string with the PII expression in the document
 * `chunkid`: the id of the document chunk it was found in
 
And it can also contain the following optional fields:
 * `subtype`: a string denoting a more concrete characterization of the PII
   (i.e. a subdivision of the main PII type)
 * `lang`: the language this PII instance refers to
 * `country`: the country this PII instance relates to, if applicable
 * `docid`: an identifier for the document the PII belongs to
 * `detector`: the index of the detector that generated the PII

Note that the PiiEntity object contains no information about the end span of
the entity value. Instead, this can be computed by adding the _length_ of the
entity (the `len()` function can be applied to the object) to the `pos`
attribute.


## Export/import

PiiEntity objects provide a `as_dict()` method that returns the descriptors of
the object as a Python dictionary.

The dictionary contains all the elements in the `fields` attribute, plus
`start` and `end` elements (computed from the `pos` attribute and the entity
length) that give the entity position in the document chunk.

There is also a class method `PiiEntity.from_dict()` that takes such a
dictionary and recreates and returns the object.

 
[*] Note that given a `pii` object:
 - `pii.type` is a `PiiEnum` object
 - `pii.fields["type"]` is a string
Both elements contain the same information, since it always holds that
`pii.fields["type"] = pii.type.name`
