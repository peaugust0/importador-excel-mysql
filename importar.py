"""Importa uma planilha (Excel ou CSV) para uma tabela MySQL.

Lê a planilha, padroniza os nomes das colunas e grava os dados na tabela.
A conexão com o banco vem de variáveis de ambiente (arquivo .env), nunca do código.
"""
import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def carregar_planilha(caminho: Path, aba: str | None) -> pd.DataFrame:
    """Lê um .xlsx/.xls (aba escolhida ou a primeira) ou um .csv (separador detectado)."""
    if caminho.suffix.lower() == ".csv":
        df = pd.read_csv(caminho, sep=None, engine="python")
    else:
        df = pd.read_excel(caminho, sheet_name=aba or 0, engine="openpyxl")
    return df.dropna(how="all")  # descarta linhas totalmente vazias


def padronizar_colunas(colunas) -> list[str]:
    """Troca espaços por _, remove símbolos e limita a 64 caracteres (limite do MySQL)."""
    nomes = []
    for coluna in colunas:
        nome = str(coluna).strip().replace(" ", "_")
        nome = re.sub(r"[^\w]", "", nome)[:64]
        nomes.append(nome)
    return nomes


def montar_url() -> URL:
    """Monta a URL de conexão a partir das variáveis de ambiente."""
    faltando = [v for v in ("DB_USER", "DB_PASSWORD", "DB_NAME") if not os.getenv(v)]
    if faltando:
        sys.exit("Faltam variáveis no .env: " + ", ".join(faltando))
    return URL.create(
        "mysql+mysqlconnector",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
    )


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser(description="Importa uma planilha para uma tabela MySQL.")
    ap.add_argument("arquivo", type=Path, help="planilha .xlsx, .xls ou .csv")
    ap.add_argument("--aba", help="nome da aba do Excel (padrão: a primeira)")
    ap.add_argument("--tabela", help="tabela de destino (padrão: nome do arquivo)")
    ap.add_argument("--modo", choices=["replace", "append"], default="replace",
                    help="replace recria a tabela; append acrescenta linhas (padrão: replace)")
    ap.add_argument("--dry-run", action="store_true",
                    help="só mostra o que seria importado, sem conectar ao banco")
    args = ap.parse_args()

    df = carregar_planilha(args.arquivo, args.aba)
    df.columns = padronizar_colunas(df.columns)
    tabela = args.tabela or re.sub(r"\W", "_", args.arquivo.stem).lower()

    print(f"{len(df)} linhas, {len(df.columns)} colunas -> tabela '{tabela}'")
    print("Colunas:", ", ".join(df.columns))
    if args.dry_run:
        print(df.head().to_string(index=False))
        return

    engine = create_engine(montar_url())
    df.to_sql(name=tabela, con=engine, if_exists=args.modo, index=False)
    print("Importação concluída.")


if __name__ == "__main__":
    main()
