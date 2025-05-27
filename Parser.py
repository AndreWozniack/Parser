from ASTNode import *
from Token import Token
from TokenType import TokenType

ll1_table = {
    # S
    ('S', 'LEFT_PARENTHESIS'):        ['Expr'],

    # Expr
    ('Expr', 'LEFT_PARENTHESIS'):     ['LEFT_PARENTHESIS', 'RPN', 'RIGHT_PARENTHESIS'],

    # RPN
    ('RPN', 'LEFT_PARENTHESIS'):      ['operand', 'RPNExpr'],
    ('RPN', 'NUMBER'):                ['operand', 'RPNExpr'],
    ('RPN', 'MEM'):                   ['MEM'],

    # RPNExpr
    ('RPNExpr', 'LEFT_PARENTHESIS'):  ['operand', 'operator'],
    ('RPNExpr', 'NUMBER'):            ['operand', 'operator'],
    ('RPNExpr', 'RES'):               ['unaryOperator'],
    ('RPNExpr', 'IF'):                ['unaryOperator'],
    ('RPNExpr', 'THEN'):              ['unaryOperator'],
    ('RPNExpr', 'ELSE'):              ['unaryOperator'],
    ('RPNExpr', 'DO'):                ['unaryOperator'],
    ('RPNExpr', 'FOR'):               ['unaryOperator'],
    ('RPNExpr', 'MEM'):               ['unaryOperator'],

    # operand
    ('operand', 'LEFT_PARENTHESIS'):  ['Expr'],
    ('operand', 'NUMBER'):            ['NUMBER'],

    # operator
    ('operator', 'OPERATOR'):         ['OPERATOR'],

    # unaryOperator
    ('unaryOperator', 'RES'):         ['RES'],
    ('unaryOperator', 'IF'):          ['IF'],
    ('unaryOperator', 'THEN'):        ['THEN'],
    ('unaryOperator', 'ELSE'):        ['ELSE'],
    ('unaryOperator', 'DO'):          ['DO'],
    ('unaryOperator', 'FOR'):         ['FOR'],
    ('unaryOperator', 'MEM'):         ['MEM'],
}

class Parser:
    def __init__(self, tokens: list[Token], debug: bool = False):
        self.tokens = tokens + [Token('$', TokenType.ERROR, -1, -1)]
        self.pos = 0
        self.debug = debug

    def current(self) -> Token:
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def token_to_term(self, tok: Token) -> str:
        if tok.value == '$':
            return '$'

        if tok.token_class in (TokenType.INTEGER_NUMBER, TokenType.REAL_NUMBER):
            return 'NUMBER'

        return tok.token_class.name


    def parse(self) -> ASTNode:
        stack = ['$', 'S']
        root  = ASTNode('S')
        node_stack = [root]

        while stack:
            top = stack.pop()
            cur = self.current()
            term = self.token_to_term(cur)

            if self.debug:
                print("────────────────────────────────────")
                print(f"STACK:       {stack + [top]!r}")
                print(f"NODE STACK:  {[n.symbol for n in node_stack]}")
                print(f"LOOKAHEAD:   {term!r}  token={cur!r}")
                print(f"TOPO DA PILHA: {top!r}")

            if top == '$':
                if term == '$':
                    return root
                else:
                    raise SyntaxError(f"EOF esperado, mas veio {term}")

            node = node_stack.pop()

            if top in {
                'LEFT_PARENTHESIS','RIGHT_PARENTHESIS',
                'NUMBER','OPERATOR',
                'MEM','RES','IF','THEN','ELSE','DO','FOR'
            }:
                if top != term:
                    raise SyntaxError(f"Esperava `{top}`, mas veio `{term}` na posição {self.pos}")
                if self.debug:
                    print(f">>> Match terminal `{top}`, consumindo token `{cur.value}`")

                val = cur.value if term in {'NUMBER','OPERATOR'} or cur.token_class == TokenType.KEYWORD else None
                child = ASTNode(top, val)
                node.children.append(child)
                self.advance()
                continue

            key = (top, term)
            if key not in ll1_table:
                raise SyntaxError(f"Sem produção para `{top}` com lookahead `{term}`")
            production = ll1_table[key]
            if self.debug:
                print(f">>> Produção: {top} -> {production}")

            # empilha filhos em ordem inversa
            children = [ASTNode(sym) for sym in production]
            node.children.extend(children)
            for sym, child in zip(reversed(production), reversed(children)):
                stack.append(sym)
                node_stack.append(child)

        raise SyntaxError("Parsing terminou sem consumir todo o input")