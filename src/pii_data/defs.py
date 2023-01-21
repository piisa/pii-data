# Format indicators for I/O
FMT_SRCDOCUMENT = "piisa:src-document:v1"
FMT_PIICOLLECTION = "piisa:pii-collection:v1"

# Format indicators for configuration files
FMT_CONFIG_PREFIX = "piisa:config:"
FMT_CONFIG_FULL = FMT_CONFIG_PREFIX + "full:v1"

# Mapping of classes to document type (as added to metadata)
DOC_TYPES = {"SequenceLocalSrcDocument": "sequence",
             "TreeLocalSrcDocument": "tree",
             "TableLocalSrcDocument": "table"}
