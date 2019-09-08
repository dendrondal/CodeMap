from pathlib import Path
from collections import namedtuple, defaultdict
import tokenize
from typing import List, Dict, Type
import networkx as nx
import ast
#TODO: Make sure that venvs are not visited

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
    Since only local imports are being analyzed, try/except logic is excluded
    **Note:** This is intelligent about the use of the 'as' keyword.
    TODO: Account for imports in parentheses
    TODO: Account for multiple periods
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
                        print('added import')
                        imported_modules.append(next_tok.string)
                    if next_tok.string == '.':
                        print('added import')
                        imported_modules.append(tokens[index+2].string)

    return imported_modules


class ImportGraph(object):

    def __init__(self):
        self.G = nx.Graph()
        self.directory = Path.cwd()
        self.local_libs = set(self.packages + self.modules)
        self.Import = namedtuple('Import', 'module name')

    @property
    def _package_paths(self) -> List[Path]:
        """Finds all __init__.py, returns parent modules"""
        packages = []
        for result in self.directory.glob('**/__init__.py'):
            packages.append(result.parent)
        return packages

    @property
    def packages(self) -> List[str]:
        """Helper function to convert posixpaths to string"""
        return [pkg.name for pkg in self._package_paths]

    @property
    def _module_paths(self) -> List[Path]:
        module_paths = []
        for pkg in self._package_paths:
            for mod in pkg.glob('*.py'):
                module_paths.append(mod)
        return module_paths

    @property
    def modules(self) -> List[str]:
        """Finds all non-init .py files, removes extensions"""
        modules = []
        for pkg in self._package_paths:
            for mod in pkg.glob('*.py'):
                modules.append(mod.stem)
                self.G.add_node(mod.stem, package=pkg.name)
        return modules

    def _get_imports(self, py_file):
        """Finds all local imports within a python file, writes them to graph"""
        with open(py_file) as f:
            root = ast.parse(f.read(), py_file)

        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                module = node.module.split('.')
                intersect = set(module) & self.local_libs
                if intersect:
                    e = [(py_file.name, i) for i in intersect]
                    self.G.add_edges_from(*e)

            elif isinstance(node, ast.ImportFrom):
                module = node.module.split('.')
                intersect = set(module) & self.local_libs
                if intersect:
                    e = [(py_file.name, i) for i in intersect]
                    self.G.add_edges_from(*e)
            else:
                continue

            for n in node.names:
                name = n.name.split('.')
                intersect = set(name) & self.local_libs
                if intersect:
                    e = [(py_file.name, i) for i in intersect]
                    self.G.add_edges_from(*e)

    def _construct_graph(self):
        for py_file in self._module_paths:
            self._get_imports(py_file)

    def output_graph(self):
        return nx.to_dict_of_dicts(self.G)

def get_imports(modules: Dict[str, List[Path]]) -> List[namedtuple]:
    links = []

    for pkg, mods in modules.items():
        for mod in mods:
            for statement in enumerate_imports(tokenizer(mod),
                                               list(modules.keys())):
                links.append(link._make([pkg, mod.stem, statement]))
    return links


def main():
    packages = get_all_packages()
    assert len(packages) > 0, "No packages found, double-check directory"
    modules = get_all_modules(packages)
    return get_imports(modules)


if __name__ == '__main__':
    print(main())

