"""
Simple script to read & write YAML Source Documents for PII Detection
"""

from argparse import ArgumentParser, Namespace

from ..helper import load_yaml
from ..doc import load_raw, dump_raw, dump_yaml



def to_raw(inputfile: str, outputfile: str, indent: int):
    """
    Convert a YAML PII Source Document to plain text
    """
    doc = load_yaml(inputfile)
    dump_raw(doc, outputfile, indent)


def from_raw(inputfile: str, outputfile: str, indent: int):
    """
    Read a raw text file and convert it to PII Source Document
    """
    doc = load_raw(inputfile, indent)
    dump_yaml(doc, outputfile, indent)


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
    if args.inputdoc.endswith(('.yml', '.yaml')):
        to_raw(args.inputdoc, args.outputdoc, args.indent)
    else:
        from_raw(args.inputdoc, args.outputdoc, args.indent)


if __name__ == '__main__':
    main()
