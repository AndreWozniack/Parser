import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict
from TokenType import TokenType
from Token import Token
from Parser import Parser

def load_tokens_by_line(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    grouped = defaultdict(list)
    for entry in raw:
        line_no = entry.get("line", "?")
        if "error" in entry:
            msg = entry["error"]
            pos = entry.get("error_position", "?")
            raise ValueError(f"Erro de lexing na linha {line_no}: {msg} (pos {pos})")
        for t in entry.get("tokens", []):
            try:
                tt = TokenType[t["token_class"]]
            except KeyError:
                raise ValueError(f"Token desconhecido '{t['token_class']}' na linha {line_no}")
            tok = Token(
                value=t["value"],
                token_class=tt,
                row=t["row"],
                column=t["column"]
            )
            grouped[line_no].append(tok)
    return grouped

def _run_parser_for_line(line_no, tokens, export_dot: bool, stem: str):
    print(f"\n--- Linha {line_no + 1} ({len(tokens)} tokens) ---")
    try:
        # parser = Parser(tokens, debug=True)
        parser = Parser(tokens)
        ast = parser.parse()
        # print("AST final:\n", ast)

        if export_dot:
            file_name = f"{stem}_line{line_no}_ast"
            out_path = Path('output') / file_name
            ast.to_graphviz(filename=str(out_path), format="png", view=False)
            print(f"  ▶ AST salva em output/{file_name}.png")

    except Exception as e:
        print(f"[PARSE ERROR] {e}")

def main():
    p = argparse.ArgumentParser(
        description="Roda o parser por linha a partir de JSON de tokens."
    )
    p.add_argument(
        "files",
        metavar="TOKENS.JSON",
        type=Path,
        nargs="+",
        help="Arquivo(s) JSON com os tokens gerados pelo lexer"
    )
    p.add_argument(
        "--dot",
        action="store_true",
        help="Exporta a AST para PNG via Graphviz"
    )
    args = p.parse_args()

    out_dir = Path('output')
    out_dir.mkdir(exist_ok=True)

    try:
        import graphviz
    except ImportError:
        print("✗ Módulo graphviz não encontrado. Rode `pip install graphviz` e instale o executável `dot`.")
        sys.exit(1)

    for fp in args.files:
        if not fp.exists():
            print(f"[ERROR] arquivo não encontrado: {fp}")
            continue

        print(f"\n=== Processando {fp.name} ===")
        try:
            tokens_by_line = load_tokens_by_line(fp)
        except ValueError as e:
            print(f"[LEX ERROR] {e}")
            continue

        stem = fp.stem
        for line_no in sorted(tokens_by_line):
            tokens = tokens_by_line[line_no]
            try:
               _run_parser_for_line(line_no, tokens, args.dot, stem)
            except Exception as e:
                print(f"[ERROR] Linha {line_no}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()