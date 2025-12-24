import streamlit as st
from collections import Counter
import pandas as pd

st.set_page_config(page_title="Bac Bo Profissional Real", layout="centered")

st.title("🎲 Bac Bo – Leitura Profissional Real")
st.caption("Somas reais | Empate 88x/25x | Leitura curta de mesa")

# =========================
# ESTADO
# =========================
if "historico" not in st.session_state:
    st.session_state.historico = []

# =========================
# ENTRADA SIMPLES
# =========================
st.subheader("➕ Registrar Rodada")

col1, col2 = st.columns(2)
with col1:
    soma_p = st.number_input("Soma Player", min_value=2, max_value=12, step=1)
with col2:
    soma_b = st.number_input("Soma Banker", min_value=2, max_value=12, step=1)

def calcula_multi_tie(soma):
    # Regras típicas de Bac Bo para multis de empate
    if soma in (2, 12):
        return "88x"
    elif soma in (3, 11):
        return "25x"
    elif soma in (4, 10):
        return "10x"
    elif soma in (5, 9):
        return "6x"
    else:  # 6,7,8
        return "4x"

if st.button("Registrar", type="primary"):
    if soma_p > soma_b:
        vencedor = "P"
        multi = "-"
    elif soma_b > soma_p:
        vencedor = "B"
        multi = "-"
    else:
        vencedor = "T"
        multi = calcula_multi_tie(soma_p)

    st.session_state.historico.append({
        "Rodada": len(st.session_state.historico) + 1,
        "P": soma_p,
        "B": soma_b,
        "V": vencedor,
        "Multi": multi
    })

# =========================
# HISTÓRICO
# =========================
st.subheader("📊 Histórico (últimas 20)")
if st.session_state.historico:
    df = pd.DataFrame(st.session_state.historico[-20:])
    st.dataframe(df, use_container_width=True, height=220)

    vencedores = [r["V"] for r in st.session_state.historico]
    total_p = vencedores.count("P")
    total_b = vencedores.count("B")
    total_t = vencedores.count("T")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Player", total_p)
    with col2:
        st.metric("Total Banker", total_b)
    with col3:
        st.metric("Total Tie", total_t)
else:
    st.info("Nenhuma rodada registrada ainda.")

# =========================
# ANÁLISE
# =========================
ultimos = st.session_state.historico[-15:]

if len(ultimos) >= 5:
    st.subheader("🧠 Análise da Mesa (curto prazo)")

    janela = ultimos[-9:]
    vencedores_validos = [r["V"] for r in janela if r["V"] != "T"]
    contagem = Counter(vencedores_validos)

    total_validos = sum(contagem.values())
    dom_p = contagem.get("P", 0) / total_validos if total_validos else 0
    dom_b = contagem.get("B", 0) / total_validos if total_validos else 0

    # Ties e multis recentes
    ties_rec = [r for r in janela if r["V"] == "T"]
    multis_altas = [r for r in ties_rec if r["Multi"] in ["88x", "25x"]]

    # Pressão de soma
    media_p = sum(r["P"] for r in janela) / len(janela)
    media_b = sum(r["B"] for r in janela) / len(janela)

    # Repetição e alternância
    repeticao = 0
    if len(vencedores_validos) >= 2 and vencedores_validos[-1] == vencedores_validos[-2]:
        repeticao = 1

    alternancia = 0
    if len(vencedores_validos) >= 4:
        seq = vencedores_validos[-4:]
        if seq[0] != seq[1] != seq[2] != seq[3]:
            alternancia = 1

    # Estado da mesa
    estado = "Estável"
    if dom_p < 0.55 and dom_b < 0.55:
        estado = "Volátil"
    if alternancia and repeticao == 0:
        estado = "Caótica"

    # Score P/B
    score_pb = 0
    score_pb += max(dom_p, dom_b) * 40
    score_pb += repeticao * 20
    score_pb += (1 if media_p > 7 or media_b > 7 else 0) * 20
    score_pb += (1 if estado == "Estável" else 0) * 20

    # Score Tie (ligado a 88x/25x)
    score_tie = 0
    score_tie += len(ties_rec) * 10
    score_tie += len(multis_altas) * 30

    # Sugestão
    if score_pb >= score_tie and score_pb >= 70 and estado == "Estável":
        lado = "PLAYER" if dom_p > dom_b else "BANKER"
        sugestao = f"ENTRAR {lado}"
        tipo = "P/B"
    elif score_tie > score_pb and score_tie >= 60:
        sugestao = "Oportunidade de TIE (88x/25x recente)"
        tipo = "TIE"
    else:
        sugestao = "SEM ENTRADA"
        tipo = "NEUTRO"

    # EXIBIÇÃO
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Dom. Player", f"{dom_p*100:.1f}%")
    with col2:
        st.metric("Dom. Banker", f"{dom_b*100:.1f}%")
    with col3:
        st.metric("Estado da Mesa", estado)
    with col4:
        st.metric("Score P/B", f"{score_pb:.0f}")

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Ties (últ. 9)", len(ties_rec))
    with col6:
        st.metric("Multis 88x/25x", len(multis_altas))

    st.subheader("🎯 Sugestão")
    if tipo == "P/B":
        st.success(sugestao)
    elif tipo == "TIE":
        st.warning(sugestao)
    else:
        st.info(sugestao)

else:
    st.info("Registre pelo menos 5 rodadas para ativar a análise.")
