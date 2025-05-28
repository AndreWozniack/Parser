from ASTNode import *
from Token import Token
from TokenType import TokenType

parse_table = {
    # S -> Expr
    ('S', 'LEFT_PARENTHESIS'):        ['Expr'],

    # Expr -> ( RPN )
    ('Expr', 'LEFT_PARENTHESIS'):     ['LEFT_PARENTHESIS', 'RPN', 'RIGHT_PARENTHESIS'],

    # RPN -> operand RPNExpr | MEM
    ('RPN', 'LEFT_PARENTHESIS'):      ['operand', 'RPNExpr'],
    ('RPN', 'NUMBER'):                ['operand', 'RPNExpr'],
    ('RPN', 'MEM'):                   ['MEM'],

    # RPNExpr -> operand operator | unaryOperator
    ('RPNExpr', 'LEFT_PARENTHESIS'):  ['operand', 'operator'],
    ('RPNExpr', 'NUMBER'):            ['operand', 'operator'],
    ('RPNExpr', 'RES'):               ['unaryOperator'],
    ('RPNExpr', 'IF'):                ['unaryOperator'],
    ('RPNExpr', 'THEN'):              ['unaryOperator'],
    ('RPNExpr', 'ELSE'):              ['unaryOperator'],
    ('RPNExpr', 'DO'):                ['unaryOperator'],
    ('RPNExpr', 'FOR'):               ['unaryOperator'],
    ('RPNExpr', 'MEM'):               ['unaryOperator'],

    # operand -> Expr | NUMBER
    ('operand', 'LEFT_PARENTHESIS'):  ['Expr'],
    ('operand', 'NUMBER'):            ['NUMBER'],

    # operator -> OPERATOR
    ('operator', 'OPERATOR'):         ['OPERATOR'],

    # unaryOperator -> RES | IF | THEN | ELSE | DO | FOR | MEM
    ('unaryOperator', 'RES'):         ['RES'],
    ('unaryOperator', 'IF'):          ['IF'],
    ('unaryOperator', 'THEN'):        ['THEN'],
    ('unaryOperator', 'ELSE'):        ['ELSE'],
    ('unaryOperator', 'DO'):          ['DO'],
    ('unaryOperator', 'FOR'):         ['FOR'],
    ('unaryOperator', 'MEM'):         ['MEM'],
}

TERMINALS = {
    'LEFT_PARENTHESIS', 'RIGHT_PARENTHESIS', 'NUMBER', 'OPERATOR',
    'MEM', 'RES', 'IF', 'THEN', 'ELSE', 'DO', 'FOR'
}


def _get_expected_tokens(non_terminal: str) -> list[str]:
    return sorted(list({
        key[1] for key in parse_table.keys() if key[0] == non_terminal
    }))


def token_to_terminal(tok: Token) -> str:
    if tok.value == '$':
        return '$'

    if tok.token_class in (TokenType.INTEGER_NUMBER, TokenType.REAL_NUMBER):
        return 'NUMBER'

    if tok.token_class == TokenType.KEYWORD:
        return tok.value.upper()

    return tok.token_class.name


class Parser:

    def __init__(self, tokens: list[Token], debug: bool = False):
        self.tokens = tokens + [Token('$', TokenType.ERROR, -1, -1)]
        self.pos = 0
        self.debug = debug

    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def advance(self):
        if self.pos < len(self.tokens) -1:
            self.pos += 1

    def _raise_syntax_error(self, message: str) -> None:
        cur = self.current_token()
        raise SyntaxError(
            f"Erro de Sintaxe [Linha {cur.row}, Coluna {cur.column}]: {message}"
        )

    def parse(self) -> ASTNode:
        stack = ['$', 'S']
        root = ASTNode('S')
        node_stack = [root]

        while stack:
            stack_top = stack.pop()
            current = self.current_token()
            lookahead = token_to_terminal(current)

            if self.debug:
                print("──────────────────────────────────────────────────")
                print(f"Pilha de Análise:  {stack + [stack_top]!r}")
                print(f"Pilha de Nós AST:  {[n.symbol for n in node_stack]}")
                print(f"Token Atual (Lookahead): {lookahead!r} (Token: {current!r})")
                print(f"Topo da Pilha:     {stack_top!r}")

            if stack_top == '$':
                if lookahead == '$':
                    print("Análise sintática concluída com sucesso!")
                    return root
                else:
                    self._raise_syntax_error(
                        f"Tokens inesperados ('{lookahead}') após o final do código válido."
                    )

            current_node = node_stack.pop()

            if stack_top in TERMINALS:
                if stack_top == lookahead:
                    if self.debug:
                        print(f">>> Match! Terminal '{stack_top}'. Consumindo token '{current.value}'.")

                    val = None
                    if lookahead in {'NUMBER', 'OPERATOR'} or current.token_class == TokenType.KEYWORD:
                        val = current.value

                    child = ASTNode(stack_top, val)
                    current_node.children.append(child)
                    self.advance()
                    continue
                else:
                    self._raise_syntax_error(
                        f"Esperava o terminal '{stack_top}', mas encontrou '{lookahead}' "
                        f"(valor: '{current.value}')."
                    )

            key = (stack_top, lookahead)
            if key in parse_table:
                production = parse_table[key]
                if self.debug:
                    print(f">>> Aplicando Produção: {stack_top} -> {' '.join(production)}")

                children = [ASTNode(sym) for sym in production]
                current_node.children.extend(children)

                for symbol, child_node in zip(reversed(production), reversed(children)):
                    stack.append(symbol)
                    node_stack.append(child_node)
            else:
                expected = _get_expected_tokens(stack_top)
                if lookahead == '$':
                    self._raise_syntax_error(
                        f"Fim de entrada inesperado. Esperava um dos seguintes: {', '.join(expected)}."
                    )
                else:
                    self._raise_syntax_error(
                        f"Token inesperado '{lookahead}' (valor: '{current.value}'). "
                        f"Esperava um dos seguintes: {', '.join(expected)}."
                    )

        self._raise_syntax_error("A análise terminou, mas a entrada não foi totalmente consumida.")
        return root