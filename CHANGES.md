# Changelog

## v. 0.5.0
 * added "extra" field to PiiEntity
 * added add_process_stage() method to PiiEntity
 * added chunks() method to PiiChunkIterator
 * added dump_yaml() function
 * fixed exception hierarchy
 * fix: error message when opening file
 * fix: in text dump protect against chunk with no text

## v. 0.4.0
 * PiiEnum base type changed to IntEnum
 * PiiEnum.STREET_ADDRESS changed to PiiEnum.LOCATION, with STREET_ADDRESS
   left as alias
 * PiiCollection improvements:
    - add_detectors() method
    - to_json() method, to make it directly serializable by CustomJSONEncoder
 * fix: PiiCollection clone should also clone the detector map
 * fix: only create a JSON encoder in PiiCollection if needed

## v. 0.3.2
 * fix: Dummy logger class

## v. 0.3.1
 * fix: ensure loaded PiiCollection objects have integer ids for Detectors
 * fix: only add lang to PiiCollection header if defined
 
## v. 0.3.0
 * PiiEntityInfo made immutable
 * added clone() class method to PiiCollection
 * refactored & improved config reading
 * new functionality in helper.io: read remote files
 * json dump parameters modified
    - allow no-indent specification
    - only close output file if we opened it
    - allow additional formatting arguments
 * added logger wrapper

## v. 0.2.0
 * DocumentChunk class refactored into a full class, with equality method and
   asdict()
 * Refactored dump code; dump to JSON
 * when dumping documents to JSON & YAML dump non-structural context fields
   (and skip structural context)
 * modified tree & sequence iteration: changed automatic id assignment
 * new class method from_dict() in PiiInstance
 * when reading a PiiCollection from file, recreate PiiInstance objects
 * wrapper load() method for PiiCollectionLoader
 * add_chunk() method for LocalSrcDocument objects (sequence, table & tree)
 * new LocalSrcDocumentFile dispatcher class
 * openfile: allow file-like objects as argument
 * fixed newlines in text output
 * added json dump to object
 * added config file management
 * new PiiEnum values
 * refactored PiiEntity; new PiiEntityInfo subclass
 * special SrcDocument metadata field "default_lang"
 * added "lang" context field to DocumentChunk, automatically copied from
   document "default_lang" if not present
 * some bugfixes

## v. 0.1.0
 * updated for data spec 0.4.0
 * added two iterators
    - iter_full, including iteration with context
    - iter_struct
 * renamed SourceDocument to SrcDocument
 * local load/dump split from SrcDocument, into a LocalSrcDocument class +
   a module function
 * added base classes for table, tree & sequence docs
 * chunk payload change from `text` to `data`, to make it more generic
 * added format indicator strings to output dump

## v. 0.0.3
 * added BaseSourceDocument and BaseSourceDocument classes
 * minor fixes in other data structures
