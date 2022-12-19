# Document chunks

A `DocumentChunk` object is the basic value generated when performing a 
"full" iteration of the document.

`DocumentChunk` is a regular Python class, with three attributes (assigned
from the constructor arguments):
 * `id`: chunk identifier
 * `data`: the chunk contents (typically a raw unicode text blob, but it could
   be anything)).
 * `context`: contextual information associated to the chunk (optional, if
   there is no context this will be `None`)

`DocumentChunk` objects have also:
 * an equality operator, that decides that two chunks are identical if their
   three attributes are the same
 * an `as_dict()` method, which returns a representation of the chunk as a
   simple Python dict


## Chunk context

The context attribute of a chunk, if present, is a Python dictionary. Its
fields depends on the document type and characteristics. We can distinguish:
 * *native* context fields: elements particular to this specific chunk,
   provided upon document creation. They will always be returned, regardless
   of the document iteration mode
 * *structural* context fields: elements that characterize the chunk within
   the document structure. They are only returned in full iterations (not
   on structural iterations) and they depend on the document type:
     - sequence documents do not have structural context fields
	 - table documents have a `column` and a `row` context field
	 - tree documents have a `level` context field, and they may also have
	   `section` field
 * *iteration* context fields provide information on _neighbouring_ chunks;
   they are the `before` and `after` fields, generated in full iteration
   when the document iteration options contain the `context` field set to 
   `True`
