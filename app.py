"""Ethereum · ¿Cómo se reconoce una cuenta fraudulenta?  Caso de análisis de SMP Soluciones.

Correr:  python -m streamlit run app.py
Datos:   datos/cuentas.csv.gz (se genera con preparar_datos.py)
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import smp

lang = smp.idioma()
st.set_page_config(page_title=("Fraude en Ethereum" if lang == "es" else "Ethereum fraud") + " · SMP Soluciones",
                   page_icon="🔎", layout="wide", initial_sidebar_state="collapsed")

ACENTO = "#9085E9"
smp.estilos(ACENTO)

# ------------------------------------------------------------------ textos
T = {
    "es": dict(
        caso="Fraude en Ethereum",
        eyebrow="Caso · Blockchain · Detección de fraude",
        titulo="¿Cómo se reconoce una cuenta <em>fraudulenta</em> en Ethereum?",
        bajada="Analizamos {n} cuentas de Ethereum, {f} de ellas marcadas como fraude, para ver en qué se comportan "
               "distinto y armar una lista simple de señales de alerta que cualquiera puede revisar.",
        f_tipo="Tipo de cuenta", f_act="Actividad (transacciones de ether)",
        tipos={"todas": "Todas", "fraude": "Fraude", "legitimas": "Legítimas"},
        act={"0": "Sin movimientos", "1-10": "1 a 10", "11-100": "11 a 100", "100+": "Más de 100"},
        fraude="Fraude", legitima="Legítima", legitimas="Legítimas", cuentas="Cuentas",
        k_cuentas="Cuentas", k_fraude="Marcadas como fraude", k_vida="Vida activa típica del fraude",
        k_eth="ETH recibido típico del fraude",
        n_cuentas="{a} con movimientos de ether", n_fraude="{p} de las cuentas",
        n_vida="legítimas: {v} · mediana", n_eth="legítimas: {v} · mediana",
        dias="{v} días", dia="día",
        tabs=["Resumen", "Comportamiento", "Tokens", "Señales de alerta", "Datos"],
        accion="Qué hacer",
        solo_un_tipo="Esta vista compara cuentas fraudulentas con legítimas. Con los filtros actuales queda un solo tipo "
                     "(o ninguna cuenta con movimientos): elige «Todas» en tipo de cuenta para verla.",
        hz1_t="Las cuentas fraudulentas viven poco y mueven poco",
        hz1_t_alt="Vida activa y volumen: fraude contra legítimas",
        hz1_x="La mitad de las fraudulentas deja de moverse antes de <b>{vf}</b>; en las legítimas, antes de <b>{vl}</b>. "
              "Reciben {ef} contra {el} (medianas).",
        hz1_a="Antes de operar con una cuenta, mirar su historial: menos de 30 días de actividad pide verificación extra.",
        hz2_t="{p} de las cuentas fraudulentas reciben de más direcciones de las que pagan",
        hz2_x="En las legítimas pasa en {pl}. La fraudulenta típica recibe de {rf} direcciones y envía a {sf}",
        hz2_x_emb=": junta dinero de muchos y lo saca por una sola salida.",
        hz2_a="Vigilar las cuentas que reciben de muchas direcciones y envían todo a una o dos: es el patrón de recolección.",
        hz3_t="Con 3 o más de 4 señales de alerta, {p} de las cuentas son fraude",
        hz3_x="Es {x} veces la tasa entre cuentas con movimientos ({b}). La regla encuentra {r} de las cuentas fraudulentas con movimientos "
              "y marca a {fp} legítimas que habría que revisar.",
        hz3_a="Usar las 4 señales como primer filtro y revisar a mano lo que cumpla 3 o más; no bloquear solo por esto.",
        r_tit="Tasa de fraude según la actividad de la cuenta",
        r_txt="Qué parte de las cuentas de cada nivel de actividad está marcada como fraude.",
        r_cero="Las <b>{n} cuentas sin movimientos</b> son todas fraude: no tienen ni una transacción de ether en los datos, "
               "así que no tienen conducta que comparar y quedan fuera de los análisis siguientes. ",
        r_alta="Entre las cuentas con más de 100 transacciones, solo <b>{p}</b> es fraude: el fraude rara vez tiene historia larga.",
        tasa="Tasa de fraude", tasa_gral="Tasa general", actividad="Actividad",
        c_tit="¿En qué se comportan distinto?",
        c_txt="Valor típico (mediana) de cada grupo, solo cuentas con movimientos. Usamos medianas porque los datos son muy "
              "desiguales: unas pocas cuentas mueven millones de ETH y arrastrarían cualquier promedio.",
        c_metricas={
            "vida_dias": ("Vida activa", "días"),
            "eth_recibido": ("ETH recibido", "ETH"),
            "eth_enviado": ("ETH enviado", "ETH"),
            "dir_recibe": ("Direcciones de las que recibe", "direcciones"),
            "dir_envia": ("Direcciones a las que envía", "direcciones"),
            "horas_entre_rec": ("Horas entre recepciones", "horas"),
        },
        mediana="Mediana", con_dato="Cuentas con dato",
        c_lect="La fraudulenta típica recibe de <b>{rf}</b> direcciones (la legítima de {rl}) pero envía a <b>{sf}</b> "
               "(la legítima a {sl}), y entre un ingreso y el siguiente pasan <b>{hf}</b> horas contra {hl}: "
               "recibe seguido, de muchos lados, y lo saca por un solo lugar.",
        c_lect_neutra="Las diferencias de comportamiento entre los grupos son pequeñas con estos filtros.",
        v_tit="¿Cuánto tiempo sigue activa la cuenta?",
        v_txt="Tiempo entre la primera y la última transacción. Cada color suma 100%.",
        v_cats=["Menos de 1 día", "1 a 7 días", "7 a 30 días", "1 a 6 meses", "Más de 6 meses"],
        v_lect="<b>{pf}</b> de las cuentas fraudulentas dejan de moverse antes de 30 días, contra {pl} de las legítimas.",
        v_ojo=" Ojo: {p1} de las legítimas duran menos de un día (cuentas usadas solo unas horas), así que la vida corta sola no basta.",
        pct_grupo="% del grupo", del_grupo="del grupo", vida="Vida activa",
        e_tit="¿Cuánto ether recibe en total?",
        e_txt="Suma de todo el ether que entró a la cuenta. Cada color suma 100%.",
        e_cats=["Menos de 1 ETH", "1 a 5 ETH", "5 a 50 ETH", "50 a 500 ETH", "Más de 500 ETH"],
        e_lect="<b>{pf}</b> de las cuentas fraudulentas recibieron menos de 5 ETH en toda su vida, contra {pl} de las legítimas.",
        eth_rec="ETH recibido",
        t_tit="Tokens que más se asocian al fraude",
        t_txt="Agrupamos las cuentas por el token ERC20 que más recibieron y medimos qué parte de cada grupo es fraude. "
              "Solo tokens recibidos por al menos el mínimo de cuentas que elijas.",
        t_min="Mínimo de cuentas por token", token="Token",
        t_lect="<b>{k}</b> de estos tokens llegan solo a cuentas fraudulentas: {lista}. Que uno de ellos sea el token "
               "principal que recibe una cuenta es una alerta fuerte.",
        t_lect_0="Con este mínimo, ningún token llega solo a cuentas fraudulentas.",
        t_nota=" Cobertura: {nf} cuentas fraudulentas no traen datos de tokens en la fuente, así que esta vista ve solo parte del fraude.",
        t_vacio="Ningún token alcanza ese mínimo de cuentas con los filtros actuales.",
        s_tit="Cuatro señales de alerta",
        s_txt="Reglas simples, sin modelos de caja negra, que cualquiera puede revisar en un explorador de bloques. "
              "Comparamos qué parte de cada grupo cumple cada señal (solo cuentas con movimientos).",
        senales={
            "s_vida": "Activa menos de 30 días",
            "s_embudo": "Recibe de más direcciones de las que paga",
            "s_poco": "Recibió menos de 5 ETH en total",
            "s_envios": "Hizo uno o ningún envío",
        },
        cumple="Cumplen la señal",
        s_lect="La señal que más separa es «{s}»: la cumplen {pf} de las fraudulentas y {pl} de las legítimas.",
        u_tit="¿Desde cuántas señales conviene revisar una cuenta?",
        u_txt="Mueve el mínimo y mira el equilibrio: más señales dan avisos más certeros, pero dejan pasar más fraude.",
        u_lbl="Revisar cuentas con al menos",
        u_fmt="{v} señales", u_fmt1="1 señal",
        u_k1="Cuentas a revisar", u_k2="De ellas, fraude", u_k3="Fraude encontrado", u_k4="Legítimas revisadas",
        u_n1="{p} de las cuentas con movimientos", u_n2="contra {b} sin la regla", u_n3="{n} de {t} cuentas fraudulentas",
        u_n4="{p} de las legítimas",
        u_graf="Tasa de fraude según cuántas señales cumple la cuenta", n_senales="Señales que cumple",
        u_lect="Sin ninguna señal, solo <b>{p0}</b> de las cuentas es fraude; con las cuatro, <b>{p4}</b>.",
        u_aviso="Los umbrales (30 días, 5 ETH) se eligieron mirando estos mismos datos y no se probaron con cuentas nuevas: "
                "es una guía para priorizar revisiones, no un veredicto.",
        x_tit="Los datos", x_txt="Las cuentas con los filtros que elegiste. Una fila por dirección.",
        x_bajar="Descargar CSV",
        x_cols=dict(address="Dirección", tipo="Tipo", transacciones="Transacciones", vida_dias="Vida activa (días)",
                    eth_recibido="ETH recibido", eth_enviado="ETH enviado", eth_saldo="Saldo ETH",
                    dir_recibe="Recibe de (direcciones)", dir_envia="Envía a (direcciones)",
                    token_recibido="Token más recibido", senales="Señales"),
        x_metodo="Cómo se hizo",
        x_metodo_txt="- **Fuente:** Ethereum Fraud Detection Dataset (Kaggle). Una fila por cuenta, con su conducta "
                     "agregada y la marca de fraude (FLAG) que trae la fuente; no la asignamos nosotros.\n"
                     "- **Limpieza:** 9.841 filas → 9.816 cuentas: 25 direcciones venían repetidas (todas legítimas) y "
                     "se dejó la primera aparición. Los nombres de token traían basura ('0', 'None', vacíos, caracteres "
                     "de control) y se tratan como \"sin dato\". El tiempo entre envíos vale 0 cuando hubo menos de dos "
                     "envíos: se tomó como \"no medible\", no como \"rápido\".\n"
                     "- **Vacíos de la fuente:** 829 cuentas, todas fraudulentas, no traen datos de tokens ERC20, y 529, "
                     "también todas fraudulentas, no tienen ninguna transacción de ether. Por eso las comparaciones de "
                     "conducta usan solo cuentas con movimientos, y no se usa \"falta el dato\" como señal. 976 cuentas "
                     "tienen saldo negativo (enviaron más de lo que la fuente registra como recibido); se dejan como vienen.\n"
                     "- **Método:** medianas por grupo (los montos son muy desiguales). Las señales son reglas fijas y su "
                     "acierto se mide en estos mismos datos, sin validación externa.\n"
                     "- **Herramientas:** SQL (SQLite) para la exploración, pandas para el cálculo y Plotly para los gráficos.",
        sin_datos="No hay cuentas con esa combinación de filtros.",
        fuente="Datos: Ethereum Fraud Detection Dataset (Kaggle)",
    ),
    "en": dict(
        caso="Ethereum fraud",
        eyebrow="Case · Blockchain · Fraud detection",
        titulo="How do you spot a <em>fraudulent</em> Ethereum account?",
        bajada="We analyzed {n} Ethereum accounts, {f} of them flagged as fraud, to see how they behave differently "
               "and build a simple list of warning signs anyone can check.",
        f_tipo="Account type", f_act="Activity (ether transactions)",
        tipos={"todas": "All", "fraude": "Fraud", "legitimas": "Legitimate"},
        act={"0": "No activity", "1-10": "1 to 10", "11-100": "11 to 100", "100+": "More than 100"},
        fraude="Fraud", legitima="Legitimate", legitimas="Legitimate", cuentas="Accounts",
        k_cuentas="Accounts", k_fraude="Flagged as fraud", k_vida="Typical fraud active life",
        k_eth="Typical ETH received by fraud",
        n_cuentas="{a} with ether activity", n_fraude="{p} of accounts",
        n_vida="legitimate: {v} · median", n_eth="legitimate: {v} · median",
        dias="{v} days", dia="day",
        tabs=["Summary", "Behavior", "Tokens", "Warning signs", "Data"],
        accion="What to do",
        solo_un_tipo="This view compares fraudulent and legitimate accounts. The current filters leave only one type "
                     "(or no accounts with activity): choose \"All\" in account type to see it.",
        hz1_t="Fraudulent accounts live briefly and move little",
        hz1_t_alt="Active life and volume: fraud versus legitimate",
        hz1_x="Half of fraudulent accounts stop moving within <b>{vf}</b>; legitimate ones, within <b>{vl}</b>. "
              "They receive {ef} versus {el} (medians).",
        hz1_a="Before dealing with an account, check its history: under 30 days of activity calls for extra verification.",
        hz2_t="{p} of fraudulent accounts receive from more addresses than they pay",
        hz2_x="Among legitimate accounts it's {pl}. The typical fraudulent account receives from {rf} addresses and sends to {sf}",
        hz2_x_emb=": it collects money from many and moves it out through a single exit.",
        hz2_a="Watch accounts that receive from many addresses and send everything to one or two: it's the collection pattern.",
        hz3_t="With 3 or more of 4 warning signs, {p} of accounts are fraud",
        hz3_x="That's {x} times the rate among active accounts ({b}). The rule finds {r} of fraudulent accounts with activity "
              "and flags {fp} legitimate ones that would need review.",
        hz3_a="Use the 4 signs as a first filter and manually review anything meeting 3 or more; don't block on this alone.",
        r_tit="Fraud rate by account activity",
        r_txt="Share of accounts at each activity level that are flagged as fraud.",
        r_cero="The <b>{n} accounts with no activity</b> are all fraud: they have not a single ether transaction in the data, "
               "so there is no behavior to compare and they are left out of the analyses that follow. ",
        r_alta="Among accounts with more than 100 transactions, only <b>{p}</b> are fraud: fraud rarely has a long history.",
        tasa="Fraud rate", tasa_gral="Overall rate", actividad="Activity",
        c_tit="How do they behave differently?",
        c_txt="Typical value (median) for each group, accounts with activity only. We use medians because the data is very "
              "uneven: a few accounts move millions of ETH and would drag any average.",
        c_metricas={
            "vida_dias": ("Active life", "days"),
            "eth_recibido": ("ETH received", "ETH"),
            "eth_enviado": ("ETH sent", "ETH"),
            "dir_recibe": ("Addresses it receives from", "addresses"),
            "dir_envia": ("Addresses it sends to", "addresses"),
            "horas_entre_rec": ("Hours between receipts", "hours"),
        },
        mediana="Median", con_dato="Accounts with data",
        c_lect="The typical fraudulent account receives from <b>{rf}</b> addresses (legitimate: {rl}) but sends to <b>{sf}</b> "
               "(legitimate: {sl}), and <b>{hf}</b> hours pass between one deposit and the next versus {hl}: "
               "it receives often, from many sources, and moves it out through one place.",
        c_lect_neutra="Behavior differences between the groups are small with these filters.",
        v_tit="How long does the account stay active?",
        v_txt="Time between the first and last transaction. Each color adds up to 100%.",
        v_cats=["Under 1 day", "1 to 7 days", "7 to 30 days", "1 to 6 months", "Over 6 months"],
        v_lect="<b>{pf}</b> of fraudulent accounts stop moving within 30 days, versus {pl} of legitimate ones.",
        v_ojo=" Note: {p1} of legitimate accounts last under a day (accounts used for just a few hours), so a short life alone is not enough.",
        pct_grupo="% of group", del_grupo="of the group", vida="Active life",
        e_tit="How much ether does it receive in total?",
        e_txt="Sum of all the ether that came into the account. Each color adds up to 100%.",
        e_cats=["Under 1 ETH", "1 to 5 ETH", "5 to 50 ETH", "50 to 500 ETH", "Over 500 ETH"],
        e_lect="<b>{pf}</b> of fraudulent accounts received under 5 ETH in their whole life, versus {pl} of legitimate ones.",
        eth_rec="ETH received",
        t_tit="Tokens most associated with fraud",
        t_txt="We grouped accounts by the ERC20 token they received most and measured what share of each group is fraud. "
              "Only tokens received by at least the minimum number of accounts you choose.",
        t_min="Minimum accounts per token", token="Token",
        t_lect="<b>{k}</b> of these tokens reach only fraudulent accounts: {lista}. If one of them is the main token "
               "an account receives, that's a strong warning.",
        t_lect_0="With this minimum, no token reaches only fraudulent accounts.",
        t_nota=" Coverage: {nf} fraudulent accounts have no token data in the source, so this view sees only part of the fraud.",
        t_vacio="No token reaches that minimum number of accounts with the current filters.",
        s_tit="Four warning signs",
        s_txt="Simple rules, no black-box models, that anyone can check in a block explorer. "
              "We compared what share of each group meets each sign (accounts with activity only).",
        senales={
            "s_vida": "Active under 30 days",
            "s_embudo": "Receives from more addresses than it pays",
            "s_poco": "Received under 5 ETH in total",
            "s_envios": "Made one or no transfers out",
        },
        cumple="Meet the sign",
        s_lect="The sign that separates best is \"{s}\": {pf} of fraudulent accounts meet it versus {pl} of legitimate ones.",
        u_tit="From how many signs should an account be reviewed?",
        u_txt="Move the minimum and watch the trade-off: more signs give sharper alerts but let more fraud through.",
        u_lbl="Review accounts with at least",
        u_fmt="{v} signs", u_fmt1="1 sign",
        u_k1="Accounts to review", u_k2="Of those, fraud", u_k3="Fraud found", u_k4="Legitimate reviewed",
        u_n1="{p} of accounts with activity", u_n2="versus {b} without the rule", u_n3="{n} of {t} fraudulent accounts",
        u_n4="{p} of legitimate accounts",
        u_graf="Fraud rate by number of signs the account meets", n_senales="Signs met",
        u_lect="With no signs, only <b>{p0}</b> of accounts are fraud; with all four, <b>{p4}</b>.",
        u_aviso="The thresholds (30 days, 5 ETH) were chosen looking at this same data and were not tested on new accounts: "
                "it's a guide to prioritize reviews, not a verdict.",
        x_tit="The data", x_txt="Accounts with the filters you chose. One row per address.",
        x_bajar="Download CSV",
        x_cols=dict(address="Address", tipo="Type", transacciones="Transactions", vida_dias="Active life (days)",
                    eth_recibido="ETH received", eth_enviado="ETH sent", eth_saldo="ETH balance",
                    dir_recibe="Receives from (addresses)", dir_envia="Sends to (addresses)",
                    token_recibido="Most received token", senales="Signs"),
        x_metodo="How it was done",
        x_metodo_txt="- **Source:** Ethereum Fraud Detection Dataset (Kaggle). One row per account, with its aggregated "
                     "behavior and the fraud flag (FLAG) provided by the source; we did not assign it.\n"
                     "- **Cleaning:** 9,841 rows → 9,816 accounts: 25 addresses were repeated (all legitimate) and the "
                     "first occurrence was kept. Token names had junk ('0', 'None', blanks, control characters) and are "
                     "treated as \"no data\". Time between transfers is 0 when there were fewer than two: it was taken as "
                     "\"not measurable\", not as \"fast\".\n"
                     "- **Gaps in the source:** 829 accounts, all fraudulent, have no ERC20 token data, and 529, also all "
                     "fraudulent, have no ether transactions at all. That's why behavior comparisons use only accounts with "
                     "activity, and \"missing data\" is not used as a sign. 976 accounts have a negative balance (they sent "
                     "more than the source records as received); they are kept as they come.\n"
                     "- **Method:** medians by group (amounts are very uneven). The signs are fixed rules and their hit "
                     "rate is measured on this same data, with no external validation.\n"
                     "- **Tools:** SQL (SQLite) for exploration, pandas for calculations and Plotly for charts.",
        sin_datos="No accounts match that combination of filters.",
        fuente="Data: Ethereum Fraud Detection Dataset (Kaggle)",
    ),
}[lang]

p = lambda v, d=1: smp.pct(v, lang, d)      # noqa: E731
n = lambda v: smp.numero(v, lang)           # noqa: E731


def eth(v):
    a = abs(v)
    dec = 0 if a >= 100 else 1 if a >= 1 else 2 if a >= 0.01 or a == 0 else 3
    return f"{smp.numero(v, lang, dec)} ETH"


def dias(v):
    return T["dias"].format(v=smp.numero(v, lang, 0 if v >= 10 else 1))


SENALES = list(T["senales"])
NOMBRE = {1: T["fraude"], 0: T["legitima"]}
COLOR = {1: smp.NEGATIVO, 0: smp.POSITIVO}


# ------------------------------------------------------------------ datos
@st.cache_data
def cargar():
    d = pd.read_csv(Path(__file__).parent / "datos" / "cuentas.csv.gz")
    d["actividad"] = pd.cut(d["transacciones"], [-1, 0, 10, 100, float("inf")],
                            labels=["0", "1-10", "11-100", "100+"]).astype(str)
    d["horas_entre_rec"] = d["min_entre_recepciones"] / 60
    d["s_vida"] = d["vida_dias"] < 30
    d["s_embudo"] = d["dir_recibe"] > d["dir_envia"]
    d["s_poco"] = d["eth_recibido"] < 5
    d["s_envios"] = d["envios"] <= 1
    d["senales"] = d[SENALES].sum(axis=1)
    return d


todo = cargar()

# ------------------------------------------------------------------ portada
smp.barra_superior(T["caso"], lang)
smp.cabecera(T["eyebrow"], T["titulo"],
             T["bajada"].format(n=n(len(todo)), f=n(todo["fraude"].sum())))

c1, c2 = st.columns([1, 1.6])
with c1:
    tipo = st.segmented_control(T["f_tipo"], list(T["tipos"]), default="todas",
                                format_func=lambda k: T["tipos"][k], key="tipo") or "todas"
with c2:
    niveles = st.pills(T["f_act"], list(T["act"]), selection_mode="multi",
                       format_func=lambda k: T["act"][k], key="niveles")

d = todo
if tipo == "fraude":
    d = d[d["fraude"] == 1]
elif tipo == "legitimas":
    d = d[d["fraude"] == 0]
if niveles:
    d = d[d["actividad"].isin(niveles)]

if d.empty:
    st.info(T["sin_datos"])
    st.stop()

act = d[d["transacciones"] > 0]           # cuentas con conducta que comparar
fr, lg = act[act["fraude"] == 1], act[act["fraude"] == 0]
ambos = not fr.empty and not lg.empty
tasa_act = act["fraude"].mean() * 100 if not act.empty else 0


def med(df, col):
    v = df[col].median()
    return None if pd.isna(v) else v


smp.kpis([
    dict(etiqueta=T["k_cuentas"], valor=n(len(d)), nota=T["n_cuentas"].format(a=n(len(act)))),
    dict(etiqueta=T["k_fraude"], valor=n(d["fraude"].sum()), tono="neg acento",
         nota=T["n_fraude"].format(p=p(d["fraude"].mean() * 100))),
    dict(etiqueta=T["k_vida"], valor=dias(med(fr, "vida_dias")) if med(fr, "vida_dias") is not None else "—",
         nota=T["n_vida"].format(v=dias(med(lg, "vida_dias")) if med(lg, "vida_dias") is not None else "—")),
    dict(etiqueta=T["k_eth"], valor=eth(med(fr, "eth_recibido")) if med(fr, "eth_recibido") is not None else "—",
         nota=T["n_eth"].format(v=eth(med(lg, "eth_recibido")) if med(lg, "eth_recibido") is not None else "—")),
])

tabs = st.tabs(T["tabs"])


def tasa_por(df, col, orden):
    g = df.groupby(col).agg(cuentas=("fraude", "size"), fraude=("fraude", "sum")).reindex(orden).dropna().reset_index()
    g["tasa"] = g["fraude"] / g["cuentas"] * 100
    return g


def barras_tasa(g, x, etiquetas, titulo_x, base):
    fig = go.Figure(go.Bar(
        x=[etiquetas.get(v, v) for v in g[x]], y=g["tasa"], marker_color=smp.NEGATIVO,
        text=[p(v, 0) for v in g["tasa"]], textposition="outside", textfont=dict(color=smp.TEXTO),
        customdata=g[["fraude", "cuentas"]],
        hovertemplate=f"<b>%{{x}}</b><br>{T['tasa']}: %{{y:.1f}}%<br>{T['fraude']}: %{{customdata[0]:,.0f}}"
                      f" / {T['cuentas']}: %{{customdata[1]:,.0f}}<extra></extra>",
    ))
    fig.add_hline(y=base, line_dash="dot", line_color=smp.TENUE, line_width=1,
                  annotation_text=f"{T['tasa_gral']} {p(base, 0)}", annotation_position="top left" if g["tasa"].iloc[0] < g["tasa"].iloc[-1] else "top right",
                  annotation_font=dict(color=smp.TENUE, size=12))
    fig.update_layout(xaxis=dict(title=titulo_x, type="category"),
                      yaxis=dict(title=T["tasa"], ticksuffix="%", range=[0, min(max(g["tasa"].max(), base) * 1.2 + 2, 115)]),
                      showlegend=False, margin=dict(t=30))
    return fig


def reparto(col, cortes, cats, titulo_x):
    """Barras agrupadas: % de cada grupo en cada rango."""
    fig = go.Figure()
    for k in (1, 0):
        g = act[act["fraude"] == k]
        r = pd.cut(g[col], cortes, labels=cats, right=False).value_counts(normalize=True).reindex(cats).fillna(0) * 100
        fig.add_bar(x=cats, y=r.values, name=NOMBRE[k], marker_color=COLOR[k],
                    text=[p(v, 0) for v in r.values], textposition="outside", textfont=dict(color=smp.TEXTO, size=11),
                    hovertemplate=f"<b>%{{x}}</b><br>{NOMBRE[k]}: %{{y:.1f}}% {T['del_grupo']}<extra></extra>")
    top = max(t.y.max() for t in fig.data)
    fig.update_layout(barmode="group", xaxis=dict(title=titulo_x, type="category"),
                      yaxis=dict(title=T["pct_grupo"], ticksuffix="%", range=[0, top * 1.22]), margin=dict(t=40))
    return fig


# ------------------------------------------------------------------ 1. resumen
with tabs[0]:
    if ambos:
        items = []
        vf, vl = fr["vida_dias"].median(), lg["vida_dias"].median()
        ef, el = fr["eth_recibido"].median(), lg["eth_recibido"].median()
        items.append(dict(
            cifra=dias(vf), tono="neg", titulo=T["hz1_t"] if (vf < vl and ef < el) else T["hz1_t_alt"],
            texto=T["hz1_x"].format(vf=dias(vf), vl=dias(vl), ef=eth(ef), el=eth(el)), accion=T["hz1_a"],
        ))
        pf, pl = fr["s_embudo"].mean() * 100, lg["s_embudo"].mean() * 100
        rf, sf = fr["dir_recibe"].median(), fr["dir_envia"].median()
        items.append(dict(
            cifra=p(pf, 0), tono="neg", titulo=T["hz2_t"].format(p=p(pf, 0)),
            texto=T["hz2_x"].format(pl=p(pl, 0), rf=n(rf), sf=n(sf)) + (T["hz2_x_emb"] if rf > sf and sf <= 1 else "."),
            accion=T["hz2_a"],
        ))
        marc = act[act["senales"] >= 3]
        if not marc.empty and tasa_act > 0:
            prec = marc["fraude"].mean() * 100
            items.append(dict(
                cifra=p(prec, 0), tono="neg", titulo=T["hz3_t"].format(p=p(prec, 0)),
                texto=T["hz3_x"].format(x=smp.numero(prec / tasa_act, lang, 1), b=p(tasa_act, 0),
                                        r=p(marc["fraude"].sum() / len(fr) * 100, 0), fp=n((marc["fraude"] == 0).sum())),
                accion=T["hz3_a"],
            ))
        for i, it in enumerate(items):
            it["n"] = f"0{i + 1}"
        smp.hallazgos(items, T["accion"])
    else:
        st.info(T["solo_un_tipo"])

    if d["fraude"].nunique() == 2 or (d["actividad"] == "0").any():
        smp.seccion(T["r_tit"], T["r_txt"])
        g = tasa_por(d, "actividad", list(T["act"]))
        smp.grafico(barras_tasa(g, "actividad", T["act"], T["actividad"], d["fraude"].mean() * 100), lang, 380)
        txt = ""
        cero = g[g["actividad"] == "0"]
        if not cero.empty and cero["tasa"].iloc[0] == 100:
            txt += T["r_cero"].format(n=n(cero["cuentas"].iloc[0]))
        alta = g[g["actividad"] == "100+"]
        if not alta.empty and alta["tasa"].iloc[0] < tasa_act:
            txt += T["r_alta"].format(p=p(alta["tasa"].iloc[0]))
        if txt:
            smp.lectura(txt)

# ------------------------------------------------------------------ 2. comportamiento
with tabs[1]:
    if not ambos:
        st.info(T["solo_un_tipo"])
    else:
        smp.seccion(T["c_tit"], T["c_txt"])
        metricas = list(T["c_metricas"].items())
        for fila in range(0, len(metricas), 3):
            cols = st.columns(3)
            for col, (m, (nombre, unidad)) in zip(cols, metricas[fila:fila + 3]):
                with col:
                    fig = go.Figure()
                    for k, g in ((1, fr), (0, lg)):
                        v = g[m].median()
                        fmt = ",.0f" if v >= 100 else ",.1f" if v >= 1 else ",.2f"
                        fig.add_bar(x=[NOMBRE[k]], y=[v], name=NOMBRE[k], marker_color=COLOR[k],
                                    text=[eth(v) if unidad == "ETH" else smp.numero(v, lang, 0 if v >= 100 or v == int(v) else 1 if v >= 1 else 2)],
                                    textposition="outside", textfont=dict(color=smp.TEXTO),
                                    customdata=[[g[m].notna().sum()]],
                                    hovertemplate=f"<b>{NOMBRE[k]}</b><br>{T['mediana']}: %{{y:{fmt}}} {unidad}"
                                                  f"<br>{T['con_dato']}: %{{customdata[0]:,.0f}}<extra></extra>")
                    top = max(t.y[0] for t in fig.data)
                    fig.update_layout(title=f"{nombre} ({unidad})", showlegend=fila == 0 and m == metricas[0][0],
                                      xaxis=dict(type="category"), yaxis=dict(range=[0, top * 1.3 if top > 0 else 1]),
                                      margin=dict(t=70), bargap=0.4)
                    smp.grafico(fig, lang, 300)
        hf, hl = fr["horas_entre_rec"].median(), lg["horas_entre_rec"].median()
        rf, rl, sf, sl = (fr["dir_recibe"].median(), lg["dir_recibe"].median(),
                          fr["dir_envia"].median(), lg["dir_envia"].median())
        if rf > rl and sf <= sl and hf < hl:
            smp.lectura(T["c_lect"].format(rf=n(rf), rl=n(rl), sf=n(sf), sl=n(sl),
                                           hf=smp.numero(hf, lang, 0), hl=smp.numero(hl, lang, 0)))
        else:
            smp.lectura(T["c_lect_neutra"])

        smp.seccion(T["v_tit"], T["v_txt"])
        smp.grafico(reparto("vida_dias", [0, 1, 7, 30, 180, float("inf")], T["v_cats"], T["vida"]), lang, 380)
        corta = (lg["vida_dias"] < 1).mean() * 100
        smp.lectura(T["v_lect"].format(pf=p(fr["s_vida"].mean() * 100, 0), pl=p(lg["s_vida"].mean() * 100, 0))
                    + (T["v_ojo"].format(p1=p(corta, 0)) if corta >= 10 else ""))

        smp.seccion(T["e_tit"], T["e_txt"])
        smp.grafico(reparto("eth_recibido", [0, 1, 5, 50, 500, float("inf")], T["e_cats"], T["eth_rec"]), lang, 380)
        smp.lectura(T["e_lect"].format(pf=p(fr["s_poco"].mean() * 100, 0), pl=p(lg["s_poco"].mean() * 100, 0)))

# ------------------------------------------------------------------ 3. tokens
with tabs[2]:
    if d["fraude"].nunique() < 2:
        st.info(T["solo_un_tipo"])
    else:
        smp.seccion(T["t_tit"], T["t_txt"])
        minimo = st.select_slider(T["t_min"], options=[10, 20, 50, 100], value=20, key="minimo")
        tk = (d.dropna(subset=["token_recibido"]).groupby("token_recibido")
              .agg(cuentas=("fraude", "size"), fraude=("fraude", "sum")).reset_index())
        tk = tk[tk["cuentas"] >= minimo]
        if tk.empty:
            st.info(T["t_vacio"])
        else:
            tk["tasa"] = tk["fraude"] / tk["cuentas"] * 100
            tk = tk.sort_values(["tasa", "cuentas"], ascending=False).head(15).iloc[::-1]
            fig = go.Figure()
            for k, share in ((1, tk["tasa"]), (0, 100 - tk["tasa"])):
                fig.add_bar(y=tk["token_recibido"], x=share, orientation="h", name=NOMBRE[k], marker_color=COLOR[k],
                            customdata=tk[["fraude", "cuentas"]].assign(leg=tk["cuentas"] - tk["fraude"])[
                                ["fraude", "leg", "cuentas"]],
                            hovertemplate=f"<b>%{{y}}</b><br>{NOMBRE[k]}: %{{x:.0f}}%<br>{T['fraude']}: %{{customdata[0]:,.0f}}"
                                          f" · {T['legitimas']}: %{{customdata[1]:,.0f}}<extra></extra>")
            fig.update_layout(barmode="stack", xaxis=dict(ticksuffix="%", range=[0, 100]),
                              yaxis=dict(type="category"), margin=dict(t=40), bargap=0.25)
            smp.grafico(fig, lang, max(320, 34 * len(tk) + 90))
            solo = tk[tk["tasa"] == 100].iloc[::-1]
            txt = (T["t_lect"].format(k=len(solo), lista=", ".join(f"{t} ({n(c)})" for t, c in zip(solo["token_recibido"], solo["cuentas"])))
                   if len(solo) else T["t_lect_0"])
            nf = int(d.loc[d["fraude"] == 1, "erc20_tx"].isna().sum())
            if nf:
                txt += T["t_nota"].format(nf=n(nf))
            smp.lectura(txt)

# ------------------------------------------------------------------ 4. señales
with tabs[3]:
    if not ambos:
        st.info(T["solo_un_tipo"])
    else:
        smp.seccion(T["s_tit"], T["s_txt"])
        cob = pd.DataFrame({"senal": SENALES, 1: [fr[s].mean() * 100 for s in SENALES],
                            0: [lg[s].mean() * 100 for s in SENALES]})
        fig = go.Figure()
        for k in (0, 1):     # legítima primero para que fraude quede arriba en barras horizontales
            fig.add_bar(y=[T["senales"][s] for s in cob["senal"]], x=cob[k], orientation="h", name=NOMBRE[k],
                        marker_color=COLOR[k], text=[p(v, 0) for v in cob[k]], textposition="outside",
                        textfont=dict(color=smp.TEXTO),
                        hovertemplate=f"<b>%{{y}}</b><br>{NOMBRE[k]}: %{{x:.1f}}% {T['cumple'].lower()}<extra></extra>")
        fig.update_layout(barmode="group", xaxis=dict(title=T["cumple"], ticksuffix="%", range=[0, 112]),
                          yaxis=dict(type="category", autorange="reversed"), margin=dict(t=40),
                          legend=dict(traceorder="reversed"))
        smp.grafico(fig, lang, 380)
        cob["dif"] = cob[1] - cob[0]
        mejor = cob.sort_values("dif", ascending=False).iloc[0]
        smp.lectura(T["s_lect"].format(s=T["senales"][mejor["senal"]], pf=p(mejor[1], 0), pl=p(mejor[0], 0)))

        smp.seccion(T["u_tit"], T["u_txt"])
        umbral = st.select_slider(T["u_lbl"], options=[1, 2, 3, 4], value=3, key="umbral",
                                  format_func=lambda v: T["u_fmt1"] if v == 1 else T["u_fmt"].format(v=v))
        marc = act[act["senales"] >= umbral]
        prec = marc["fraude"].mean() * 100 if not marc.empty else 0
        enc = int(marc["fraude"].sum())
        fp = int((marc["fraude"] == 0).sum())
        smp.kpis([
            dict(etiqueta=T["u_k1"], valor=n(len(marc)), nota=T["u_n1"].format(p=p(len(marc) / len(act) * 100, 0))),
            dict(etiqueta=T["u_k2"], valor=p(prec, 0), tono="neg acento", nota=T["u_n2"].format(b=p(tasa_act, 0))),
            dict(etiqueta=T["u_k3"], valor=p(enc / len(fr) * 100, 0), nota=T["u_n3"].format(n=n(enc), t=n(len(fr)))),
            dict(etiqueta=T["u_k4"], valor=n(fp), nota=T["u_n4"].format(p=p(fp / len(lg) * 100, 0))),
        ])
        g = tasa_por(act, "senales", [0, 1, 2, 3, 4])
        g["senales"] = g["senales"].astype(int).astype(str)
        fig = barras_tasa(g, "senales", {}, T["n_senales"], tasa_act)
        fig.update_layout(title=T["u_graf"], margin=dict(t=60))
        smp.grafico(fig, lang, 380)
        gi = g.set_index("senales")["tasa"]
        if {"0", "4"} <= set(gi.index) and gi["4"] > gi["0"]:
            smp.lectura(T["u_lect"].format(p0=p(gi["0"]), p4=p(gi["4"], 0)) + " " + T["u_aviso"])
        else:
            smp.lectura(T["u_aviso"])

# ------------------------------------------------------------------ 5. datos
with tabs[4]:
    smp.seccion(T["x_tit"], T["x_txt"])
    vista = d.assign(tipo=d["fraude"].map(NOMBRE))[list(T["x_cols"])].sort_values("eth_recibido", ascending=False)
    st.dataframe(vista, hide_index=True, width="stretch", height=420,
                 column_config={
                     **T["x_cols"],
                     "address": st.column_config.TextColumn(T["x_cols"]["address"], width="medium"),
                     "vida_dias": st.column_config.NumberColumn(T["x_cols"]["vida_dias"], format="%.1f"),
                     "eth_recibido": st.column_config.NumberColumn(T["x_cols"]["eth_recibido"], format="%.2f"),
                     "eth_enviado": st.column_config.NumberColumn(T["x_cols"]["eth_enviado"], format="%.2f"),
                     "eth_saldo": st.column_config.NumberColumn(T["x_cols"]["eth_saldo"], format="%.4f"),
                 })
    st.download_button(T["x_bajar"], vista.rename(columns=T["x_cols"]).to_csv(index=False).encode("utf-8"),
                       "cuentas_ethereum.csv", "text/csv")
    with st.expander(T["x_metodo"]):
        st.markdown(T["x_metodo_txt"])

smp.pie(lang, T["fuente"])
