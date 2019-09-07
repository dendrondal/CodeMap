from pathlib import Path
from collections import namedtuple
import tokenize
from typing import List, Dict, Type


def get_all_py_files() -> List[Path]:
    """Recursively walks down cwd, finds all .py files"""
    p = Path.cwd()
    return list(p.glob('**/*.py'))


def tokenizer(filepath: Path) -> List[namedtuple]:
    """Tokenizes *source* and returns the tokens as a list of lists."""
    return [a for a in tokenize.generate_tokens(open(filepath).readline)]


def enumerate_imports(tokens: List[namedtuple], local_pkgs: List[str]):
    """
    Iterates over *tokens* and returns a list of all imported modules.

    **Note:** This is intelligent about the use of the 'as' keyword.
    TODO: Account for imports in parentheses
    """
    imported_modules = []
    import_line = False
    for index, tok in enumerate(tokens):
        if tok.type == tokenize.NEWLINE:
            import_line = False
        elif tok.string == "import":
            import_line = True
        elif import_line:
            next_tok = tokens[index+1]
            if tok.type == tokenize.NAME and next_tok.string != 'as':
                if next_tok.string not in imported_modules:
                    if next_tok.string in local_pkgs:
                        imported_modules.append(next_tok.string)
                    if next_tok.string == '.':
                        imported_modules.append(tokens[index+2].string)

    return imported_modules


def get_all_packages(file_list: List[Path]) -> List[str]:
    """Finds all __init__.py, returns parent modules"""
    packages = []
    for file in file_list:
        if file.name == '__init__.py':
            packages.append(file.parent.name())
    return packages


def get_all_modules(file_list: List[Path]) -> List[str]:
    """Finds all non-init .py files, removes extensions"""
    modules = []
    for file in file_list:
        if file.name is not '__init__.py':
            modules.append(file.stem)
    return modules


def main(packages, modules, imports):

if __name__ == '__main__':
    pyfile = Path.cwd()/'janitor'/'chemistry.py'
    tokens = listified_tokenizer(str(pyfile))
    print(tokens)
    print(enumerate_imports(tokens))
