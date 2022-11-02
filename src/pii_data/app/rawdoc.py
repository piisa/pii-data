"""
Simple script to convert a YAML Source Document to raw text
"""

from argparse import ArgumentParser, Namespace

from ..types.localdoc import LocalSrcDocumentFile


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description='Read a YAML PII Source Doc and write it out (to either YAML or to plain raw text')
    args.add_argument('inputdoc')
    args.add_argument('outputdoc', help="output file (the file extension will decide the format)")
    args.add_argument('--indent', type=int, default=0, help="for tree documents and plain text output, the indent for each level")
    args.add_argument('--context-fields', nargs="+", metavar="FIELDNAME",
                      help="context fields to add")
    return args.parse_args()


def main(args: Namespace = None):

    if not args:
        args = parse_args()

    # Read document
    doc = LocalSrcDocumentFile(args.inputdoc)

    # Write it
    doc.dump(args.outputdoc, context_fields=args.context_fields,
             indent=args.indent)


if __name__ == '__main__':
    main()
