# Importador de planilha para MySQL

Script em Python que lê uma planilha (Excel ou CSV), padroniza os nomes das colunas e grava os dados em uma tabela MySQL. Nasceu para trocar a importação manual de planilhas por um comando repetível.

> Os dados de `dados_exemplo/` são **fictícios**. Nenhum dado real faz parte deste repositório.

## O que ele faz

1. Lê `.xlsx`, `.xls` ou `.csv` (o separador do CSV é detectado sozinho).
2. Descarta linhas totalmente vazias.
3. Padroniza as colunas: espaços viram `_`, símbolos são removidos e o nome é limitado a 64 caracteres (limite do MySQL).
4. Grava na tabela escolhida, recriando-a (`replace`) ou acrescentando linhas (`append`).

A conexão vem de variáveis de ambiente (`.env`), nunca do código.

## Como usar

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha usuário, senha e nome do banco
```

Ver o que seria importado, sem tocar no banco:

```bash
python importar.py dados_exemplo/cobrancas_exemplo.csv --dry-run
```

Importar de verdade:

```bash
python importar.py dados_exemplo/cobrancas_exemplo.csv --tabela cobrancas_exemplo
python importar.py minha_planilha.xlsx --aba "Dados" --modo append
```

## Cuidados

- `--modo replace` apaga e recria a tabela de destino. Use `append` para manter o que já existe.
- Planilhas reais ficam fora do git (`*.xlsx` está no `.gitignore`).
- Este é um script pequeno e sem testes automatizados.

## Tecnologias

Python 3.10+, pandas, openpyxl, SQLAlchemy, mysql-connector-python, python-dotenv.
