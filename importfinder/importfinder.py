from pathlib import Path
from collections import namedtuple
from typing import List
import networkx as nx
import ast
from jinja2 import Environment, FileSystemLoader
import holoviews as hv
from holoviews import opts, dim
import pandas as pd
# TODO: Make sure that venvs are not visited


class ImportGraph(object):

    def __init__(self, directory=Path.cwd()):
        self.G = nx.Graph()
        self.directory = directory
        self.local_libs = set(self.packages + self.modules)
        self.Import = namedtuple('Import', 'nodes links parents')

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
                if not str(mod).startswith('__init__'):
                    module_paths.append(mod)
        return module_paths

    @property
    def modules(self) -> List[str]:
        """Finds all non-init .py files, removes extensions"""
        modules = []
        for pkg in self._package_paths:
            for mod in pkg.glob('*.py'):
                if not str(mod).startswith('__init__'):
                    modules.append(mod.stem)
                    self.G.add_node(mod.stem, package=pkg.name)
        return modules

    def _get_imports(self, py_file):
        """Finds all local imports within a python file, writes them to graph"""
        with open(py_file) as f:
            root = ast.parse(f.read(), py_file)

        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                continue

            elif isinstance(node, ast.ImportFrom) and node.module is None:
                node.visit()


            elif isinstance(node, ast.ImportFrom):
                module = node.module.split('.')
                intersect = set(module) & self.local_libs
                if intersect:
                    for i in intersect:
                        self.G.add_edge(py_file.stem, i)

            else:
                continue

            for n in node.names:
                name = n.name.split('.')
                intersect = set(name) & self.local_libs
                if intersect:
                    for i in intersect:
                        self.G.add_edge(py_file.stem, i)

    def _construct_graph(self):
        for py_file in self._module_paths:
            self._get_imports(py_file)

    def output_graph(self):
        self._construct_graph()
        graph_data = []
        for node in self.G.nodes(data=True):
            for edge in self.G.edges():
                try:
                    graph_data.append({'source': edge[0],
                                       'target': edge[1],
                                       'weight': 1,
                                       'node': node[0],
                                       'package': node[1]['package'],
                                       })
                except KeyError:
                    #takes care of base module imports
                    pass
        df = pd.DataFrame(graph_data)
        return df



if __name__ == '__main__':
    test = ImportGraph(directory=Path('/home/dal/PycharmProjects/pyjanitor_fork/janitor'))
    df = test.output_graph()
    hv.extension('bokeh')
    defaults = dict(width=1000, height=1000, padding=0.1)
    chord = hv.Chord((df[['source', 'target', 'weight']],
                      df[['node', 'package']]))
    chord.opts(
        opts.Chord(cmap='Category20', edge_cmap='Category20',
                   edge_color=dim('source').str(), labels='node',
                   node_color=dim('package').str(), width=1000, height=1000)
    )
    hv.save(chord, 'test.html')
