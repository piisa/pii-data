# Format indicators for I/O
FMT_SRCDOCUMENT = "piisa:src-document:v1"
FMT_PIICOLLECTION = "piisa:pii-collection:v1"

# Mapping of classes to document type (as added to metadata)
DOC_TYPES = {"SequenceLocalSrcDocument": "sequence",
             "TreeLocalSrcDocument": "tree",
             "TableLocalSrcDocument": "table"}

# Official struture context fields
CTX_FIELDS = ["before", "after",                # neighboring chunks
              "document", "dataset",            # general metadata
              "section", "level",               # metadata for tree documents
              "column", "row"]                  # metadata for table documents
