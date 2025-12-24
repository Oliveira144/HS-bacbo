import streamlit as st
from collections import Counter
import pandas as pd

st.set_page_config(page_title="Bac Bo Profissional v3 – LIGHTNING", layout="wide")

st.title("🎲 Bac Bo Lightning – Trader Completo")
st.caption("Roadmaps + Multiplicadores 88x/25x + Gestão Profissional")

# =========================
# ESTADO E BANCA
# =========================
if "historico" not in st.session_state:
    st.session_state.historico = []
if "banca" not in st.session_state:
    st.session_state.banca = 1000
if "unidade" not in st.session_state:
    st.session_state.unidade = 20

# =========================
# ENTRADA COMPLETA (COM TIE MULTI)
# =========================
st.subheader("➕ Registrar Rodada Completa")
col1, col2, col3, col4 = st.columns(4)
with col1:
    soma_p = st.number_input("Soma Player", min_value=2, max_value=12, key="soma_p")
with col2:
    soma_b = st.number_input("Soma Banker", min_value=2, max_value=12, key="soma_b")
with col3:
    st.session_state.banca = st.number_input("Banca Atual (R$)", min_value=0.0, value=st.session_state.banca, key="banca_input")
with col4:
    st.session_state.unidade = st.number_input("Unidade Base (R$)", min_value=1.0, value=st.session_state.unidade, key="unidade_input")

if st.button("➕ Registrar", type="primary"):
    if soma_p > soma_b:
        vencedor = "P"
        multi_tie = "-"  # Sem multi em P/B
    elif soma_b > soma_p:
        vencedor = "B"
        multi_tie = "-"
    else:
        vencedor = "T"
        # CALCULA MULTI TIE 88x/25x baseado nas somas
        if soma_p == 2 or soma_p == 12:
            multi_tie = "88x"
        elif soma_p == 3 or soma_p == 11:
            multi_tie = "25x"
        elif soma_p == 4 or soma_p == 10:
            multi_tie = "10x"
        elif soma_p == 5 or soma_p == 9:
            multi_tie = "6x"
        else:  # 6,7,8
            multi_tie = "4x"

    st.session_state.historico.append({
        "rodada": len(st.session_state.historico) + 1,
        "P": soma_p, "B": soma_b, "V": vencedor, "Multi": multi_tie
    })
    st.success(f"Rodada {len(st.session_state.historico)}: {vencedor} | Multi: {multi_tie}")

# =========================
# ROADMAP VISUAL + MULTIS
# =========================
st.subheader("📊 Roadmap Completo (últimas 20)")
if st.session_state.historico:
    ultimas_20 = st.session_state.historico[-20:]
    df_roadmap = pd.DataFrame(ultimas_20)
    st.dataframe(df_roadmap, use_container_width=True, height=120)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_p = sum(1 for r in ultimas_20 if r["V"] == "P")
        st.metric("Player", total_p)
    with col2:
        total_b = sum(1 for r in ultimas_20 if r["V"] == "B")
        st.metric("Banker", total_b)
    with col3:
        total_t = sum(1 for r in ultimas_20 if r["V"] == "T")
        st.metric("Tie", total_t)
    with col4:
        multis_88 = sum(1 for r in ultimas_20 if r["Multi"] == "88x")
        st.metric("88x Oportun.", multis_88)

# =========================
# ANÁLISE LIGHTNING PRO
# =========================
if len(st.session_state.historico) >= 6:
    st.subheader("🧠 Análise Profissional")
    
    janela_9 = st.session_state.historico[-9:]
    janela_6 = st.session_state.historico[-6:]
    vencedores_9 = [r["V"] for r in janela_9 if r["V"] != "T"]
    vencedores_6 = [r["V"] for r in janela_6 if r["V"] != "T"]
    
    # DOMINÂNCIA P/B
    contagem = Counter(vencedores_9)
    total_validos = sum(contagem.values())
    dom_p = contagem.get("P", 0) / total_validos if total_validos else 0
    dom_b = contagem.get("B", 0) / total_validos if total_validos else 0
    
    # ROADMAP PATTERNS
    streak_p = sum(1 for i in range(len(vencedores_9)-3) if vencedores_9[i:i+4] == ['P','P','P','P'])
    streak_b = sum(1 for i in range(len(vencedores_9)-3) if vencedores_9[i:i+4] == ['B','B','B','B'])
    chop_count = sum(1 for i in range(len(vencedores_6)-1) if vencedores_6[i] != vencedores_6[i+1])
    
    # FREQUÊNCIA TIE (SINAL DE MESA)
    ties_recentes = sum(1 for r in janela_9 if r["V"] == "T")
    multi_alta = sum(1 for r in janela_9 if r["Multi"] in ["88x", "25x"])
    
    # MODO DA MESA (COM TIE)
    if streak_p >= 1 and dom_p > 0.6:
        modo = "🔴 STREAK PLAYER"
        tendencia = "P"
    elif streak_b >= 1 and dom_b > 0.6:
        modo = "🔵 STREAK BANKER"
        tendencia = "B"
    elif chop_count >= 4 or ties_recentes >= 2:
        modo = "➡️ CHOP/TIE ZONE"
        tendencia = None
    elif dom_p > 0.65:
        modo = "📈 Player Forte"
        tendencia = "P"
    elif dom_b > 0.65:
        modo = "📈 Banker Forte"
        tendencia = "B"
    elif multi_alta >= 1:
        modo = "⚡ Multis Altas (88x/25x)"
        tendencia = "T"  # Preparar TIE quando multi alta recente
    else:
        modo = "⚖️ Neutro"
        tendencia = None
    
    # PRESSÃO DE SOMA
    media_p = sum(r["P"] for r in janela_9) / len(janela_9)
    media_b = sum(r["B"] for r in janela_9) / len(janela_9)
    somas_extremas = sum(1 for r in janela_9 if r["P"] in [2,12] or r["B"] in [2,12])
    
    # SCORE PROFISSIONAL (AGORA COM TIE)
    score_pb = 0
    score_tie = 0
    
    # Score P/B
    score_pb += max(dom_p, dom_b) * 40
    score_pb += min(streak_p + streak_b, 2) * 15
    score_pb += (1 if abs(media_p - media_b) > 1.5 else 0) * 10
    
    # Score TIE (88x/25x)
    score_tie += ties_recentes * 15
    score_tie += multi_alta * 25
    score_tie += somas_extremas * 20
    
    score_final = max(score_pb, score_tie)
    
    # GESTÃO DE STAKE
    if score_final >= 80:
        multiplicador = 2.0 if tendencia != "T" else 1.0  # TIE stake menor
        força = "FORTE"
    elif score_final >= 65:
        multiplicador = 1.5 if tendencia != "T" else 0.5
        força = "MÉDIA"
    elif score_final >= 55:
        multiplicador = 1.0 if tendencia != "T" else 0.3
        força = "LEVE"
    else:
        multiplicador = 0
        força = "AGUARDAR"
    
    stake_sugerida = st.session_state.unidade * multiplicador
    
    # SUGESTÃO FINAL
    if multiplicador > 0 and tendencia:
        if tendencia == "T":
            sugestao = f"TIE {multi_alta>0 and 'HIGH MULTI' or ''} | R$ {stake_sugerida:.0f}"
        else:
            sugestao = f"APOSTAR {tendencia} | R$ {stake_sugerida:.0f}"
        cor = "success" if score_final >= 70 else "warning"
    else:
        sugestao = f"{força} | Score: {score_final:.0f}"
        cor = "secondary"
    
    # DISPLAY PRO
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Dom P", f"{dom_p*100:.0f}%")
    with col2: st.metric("Dom B", f"{dom_b*100:.0f}%")
    with col3: st.metric("Modo", modo)
    with col4: st.metric("Score", f"{score_final:.0f}")
    with col5: st.metric("Ties Rec.", ties_recentes)
    
    st.subheader("🎯 Operação Recomendada")
    if cor == "success":
        st.success(sugestao)
    elif cor == "warning":
        st.warning(sugestao)
    else:
        st.info(sugestao)
    
    st.caption(f"💰 Stake: R$ {stake_sugerida:.0f} | Banca: R$ {st.session_state.banca:.0f} | {multi_alta}x Multis 88x/25x recentes")

else:
    st.info("📝 6+ rodadas para análise completa.")

# AVISO FINAL
st.error("⚠️ House Edge existe. TIE 88x/25x = RTP 95.52%. Gestão obrigatória!")
