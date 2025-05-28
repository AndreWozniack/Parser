import argparse
import json
from Token import Token
from Lexer import Lexer, LexicalError

def token_to_dict(token: Token) -> dict:
    return token.tokenToDict()

def print_tokens(tokens: list[Token], line_counter: int, line, error=None):
    line_separator = "-=" * 25
    formatted_line = line.rstrip("\n")

    print(f"\n{line_separator}")
    print(f" Line {line_counter:3d} - {formatted_line}")
    print(f"{line_separator}")

    if tokens:
        for token in tokens:
            print(f"{token.token_class.name:<20} | {token.value:<5} | {token.row}:{token.column:<5}")
    else:
        print("No valid tokens found.")

    if error:
        exc, pos = error
        msg = str(exc)
        print(f"\nError: {msg} {line_counter}:{pos}")
        print(f"{formatted_line}")
        print(" " * pos + "^-- Error here")

    print(f"{line_separator}\n")

def tokenize_file(
        input_path: str,
        save_json: bool = False,
        output_path: str = "tokens_output.json",
        raw: bool = False
) -> list[Token]:
    token_list = []
    output_data = []
    line_counter = 0

    with open(input_path, 'r') as file:
        lines = file.readlines()

    in_multiline_comment = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue
        if stripped.startswith("/*"):
            in_multiline_comment = True
            continue
        if in_multiline_comment:
            if "*/" in stripped:
                in_multiline_comment = False
            continue

        if stripped.startswith("#") or stripped.startswith("//"):
            continue

        lexer = Lexer(stripped, line_counter)
        try:
            tokens = lexer.tokenize()
            error = None

        except LexicalError as e:
            tokens = lexer.tokens
            error = (e, e.position)
        except Exception as e:
            tokens = lexer.tokens
            error = (e, lexer.index)

        if raw:
            for tok in tokens:
                print(tok)
            print()
        else:
            print_tokens(tokens, line_counter, line, error=error)


        entry = {"line": line_counter}
        if tokens:
            entry["tokens"] = [token_to_dict(tok) for tok in tokens]
        if error:
            entry["error"] = str(error[0])
            entry["error_position"] = error[1]
        output_data.append(entry)

        token_list.extend(tokens)
        line_counter += 1

    if save_json:
        with open(output_path, "w", encoding="utf-8") as out_file:
            json.dump(output_data, out_file, indent=4)
        print(f"\n✅ Tokens salvos em {output_path}")

    return token_list

def main():
    parser = argparse.ArgumentParser(description="Lexer Tokenizer")
    parser.add_argument(
        "--file",
        required=True,
        help="Arquivo de entrada com código-fonte"
    )
    parser.add_argument(
        "-s", "--save",
        dest="save_json",
        action="store_true",
        help="Salvar tokens em formato JSON"
    )
    parser.add_argument(
        "--output",
        default="tokens_output.json",
        help="Caminho do arquivo de saída JSON (opcional)"
    )
    parser.add_argument(
        "-r", "--raw",
        action="store_true",
        help="Imprime apenas os tokens, um por linha, e pula linha após cada input"
    )

    args = parser.parse_args()

    tokenize_file(
        args.file,
        args.save_json,
        args.output,
        raw=args.raw
    )

if __name__ == '__main__':
    main()