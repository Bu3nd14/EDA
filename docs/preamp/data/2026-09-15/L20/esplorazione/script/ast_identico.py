#!/usr/bin/env python3
"""ast_identico.py - L20: the edit to gain_block.py is comments only.

Usage: python3 ast_identico.py <before.py> <after.py>
Exit 0 if the two files parse to the same AST (comments are not in the AST),
1 if they differ, 2 on a parse error. Made to fall by passing a copy with one
value changed.
"""
import ast
import sys


def dump(path):
    with open(path) as f:
        return ast.dump(ast.parse(f.read()), include_attributes=False)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        a, b = dump(argv[1]), dump(argv[2])
    except SyntaxError as e:
        print(f"PARSE ERROR: {e}")
        return 2
    if a == b:
        print(f"AST IDENTICAL: {argv[1]} == {argv[2]} ({len(a)} chars of dump)")
        return 0
    print(f"AST DIFFERS: {argv[1]} != {argv[2]}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
