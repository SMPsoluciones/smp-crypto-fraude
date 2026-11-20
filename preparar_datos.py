"""Genera datos/cuentas.csv.gz a partir de fraud_crypto.db (tabla transactions).

Una fila por cuenta (dirección) de Ethereum, con FLAG = 1 fraude / 0 legítima.
Problemas del origen que se corrigen aquí:
- 25 direcciones aparecen dos veces (todas legítimas). Las copias solo difieren, a veces, en el
  nombre del token más enviado o recibido. Se deja la primera aparición.
- Los nombres de columna traen espacios al inicio (' Total ERC20 tnxs'); se pasan a snake_case.
- Las 23 columnas de tokens ERC20 vienen vacías ('') en 829 cuentas, todas fraudulentas:
  quedan como "sin dato" (NaN), no como cero.
- Los nombres de token traen basura: '0' (la cuenta no usó tokens), 'None', '', ' ', "''", '\\x01'.
  Todo eso queda como "sin dato".
- El tiempo promedio entre envíos (o recepciones) vale 0 cuando la cuenta hizo menos de dos;
  ese 0 no significa "rápido" sino "no se puede medir", así que queda como NaN.
Se corre una sola vez: python preparar_datos.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
with sqlite3.connect(AQUI / "fraud_crypto.db") as con:
    crudo = pd.read_sql("SELECT * FROM transactions", con)

crudo.columns = crudo.columns.str.strip()
dups = crudo["Address"].duplicated().sum()
d = crudo.drop_duplicates("Address", keep="first").copy()

erc20 = pd.to_numeric(d["Total ERC20 tnxs"], errors="coerce")   # '' -> NaN
BASURA = {"", "0", "None", "''", "\x01"}


def token(s):
    s = s.astype(str).str.strip()
    return s.where(~s.isin(BASURA))


c = pd.DataFrame({
    "address": d["Address"],
    "fraude": d["FLAG"].astype(int),
    "transacciones": d["total transactions (including tnx to create contract"].astype(int),
    "envios": d["Sent tnx"].astype(int),
    "recepciones": d["Received Tnx"].astype(int),
    "vida_dias": (d["Time Diff between first and last (Mins)"] / 1440).round(3),
    "min_entre_envios": d["Avg min between sent tnx"].where(d["Sent tnx"] >= 2),
    "min_entre_recepciones": d["Avg min between received tnx"].where(d["Received Tnx"] >= 2),
    "dir_recibe": d["Unique Received From Addresses"].astype(int),
    "dir_envia": d["Unique Sent To Addresses"].astype(int),
    "eth_recibido": d["total ether received"].round(6),
    "eth_enviado": d["total Ether sent"].round(6),
    "eth_saldo": d["total ether balance"].round(6),
    "contratos_creados": d["Number of Created Contracts"].astype(int),
    "erc20_tx": erc20,
    "token_recibido": token(d["ERC20_most_rec_token_type"]),
    "token_enviado": token(d["ERC20 most sent token type"]),
})

(AQUI / "datos").mkdir(exist_ok=True)
c.to_csv(AQUI / "datos" / "cuentas.csv.gz", index=False, compression="gzip")

print(f"{len(crudo)} filas -> {len(c)} cuentas ({dups} direcciones duplicadas quitadas)")
print(f"fraude: {c.fraude.sum()} ({c.fraude.mean():.1%}) · sin movimientos de ether: {(c.transacciones == 0).sum()}"
      f" · sin datos ERC20: {c.erc20_tx.isna().sum()} · saldo negativo: {(c.eth_saldo < 0).sum()}")
print(f"token recibido con nombre: {c.token_recibido.notna().sum()} · nulos totales:\n{c.isna().sum()[lambda s: s > 0]}")
