from graphviz import *

class ASTNode:
    def __init__(self, symbol, value=None):
        self.symbol = symbol
        self.value = value
        self.children = []

    def __repr__(self, level=0):
        indent = "  " * level
        if self.value is not None:
            return f"{indent}{self.symbol}({self.value})"
        s = f"{indent}{self.symbol}\n"
        for c in self.children:
            s += c.__repr__(level+1) + "\n"
        return s.rstrip()

    def to_graphviz(self, filename="ast", format="png", view=False):

        dot = Digraph(comment="Abstract Syntax Tree", format=format)
        self._add_to_graph(dot)
        dot.render(filename, view=view)

    def _add_to_graph(self, dot: Digraph, parent_id: str = None):
        node_id = str(id(self))
        label = self.symbol + (f"\n{self.value}" if self.value is not None else "")
        dot.node(node_id, label=label)
        if parent_id is not None:
            dot.edge(parent_id, node_id)
        for child in self.children:
            child._add_to_graph(dot, node_id)