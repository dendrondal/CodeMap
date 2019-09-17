from pathlib import Path
from collections import namedtuple
from typing import List
import networkx as nx
import ast
from jinja2 import Environment, FileSystemLoader
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
                continue

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
        graph_data = {'nodes': [], 'links': []}
        for node in self.G.nodes(data=True):
            for edge in self.G.edges():
                print(node[1], edge)
                try:
                    graph_data['nodes'].append({'name': node[0],
                                                'group': node[1]['package']})
                    graph_data['links'].append({'source': edge[0],
                                                'target': edge[1]})
                except KeyError:
                    #takes care of base module imports
                    pass
        print(graph_data)
        return graph_data



if __name__ == '__main__':
    test = ImportGraph(directory=Path('/home/dal/PycharmProjects/pyjanitor_fork')).output_graph()
    env = Environment(loader=FileSystemLoader('../templates'))
    template = env.get_template('hive.html')
    output = template.render(nodes=test['nodes'], links=test['links'])
    with open('test_graph.html', 'w') as f:
        f.write(output)
