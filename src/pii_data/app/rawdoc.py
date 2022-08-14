"""
Simple script to convert a YAML Source Document to raw text
"""

from argparse import ArgumentParser, Namespace

from ..helper import load_yaml
from ..helper.io import base_extension
from ..doc import dump_text, dump_yaml
from ..types.localdoc import LocalSrcDocument


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description='Convert from YAML PII Source Doc to plain raw text or viceversa')
    args.add_argument('inputdoc')
    args.add_argument('outputdoc')
    args.add_argument('--indent', type=int, default=0)
    return args.parse_args()


def main(args: Namespace = None):

    if not args:
        args = parse_args()

    # Read document
    doc = LocalSrcDocument(args.inputdoc)

    # Write it
    ext2 = base_extension(args.outputdoc)
    if ext2 in ('.yml', '.yaml'):
        dump_yaml(doc, args.outputdoc)
    else:
        dump_text(doc, args.outputdoc, args.indent)


if __name__ == '__main__':
    main()
