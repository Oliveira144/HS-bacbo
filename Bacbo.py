import streamlit as st
from collections import Counter

st.set_page_config(page_title="Bac Bo – Painel Profissional", layout="centered")

st.title("🎲 Bac Bo – Painel Profissional por Cores")
st.caption("Entrada por botões de cor | Streak, Zigzag, Block, Tie Zone")

# =========================
# ESTADO
# =========================
if "history" not in st.session_state:
    st.session_state.history = []  # sequência de 'P','B','T'

# =========================
# ENTRADA POR COR (BOTÕES)
# =========================
st.subheader("➕ Registrar rodada (cor)")

col1, col2, col3 = st.columns(3)
clicked = None

with col1:
    if st.button("PLAYER", type="primary"):
        clicked = "P"
with col2:
    if st.button("BANKER"):
        clicked = "B"
with col3:
    if st.button("TIE"):
        clicked = "T"

if clicked:
    st.session_state.history.append(clicked)

# =========================
# HISTÓRICO VISUAL
# =========================
st.subheader("📊 Roadmap simples (últimas 40)")

seq = st.session_state.history

if seq:
    ult = seq[-40:]
    st.write("Sequência:", " ".join(ult))

    total_p = ult.count("P")
    total_b = ult.count("B")
    total_t = ult.count("T")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Player (P)", total_p)
    with c2:
        st.metric("Banker (B)", total_b)
    with c3:
        st.metric("Tie (T)", total_t)
else:
    st.info("Ainda sem rodadas.")

# =========================
# ANÁLISE PROFISSIONAL
# =========================
if len(seq) >= 6:
    st.subheader("🧠 Leitura Profissional de Mesa")

    # só P/B para leitura de fluxo
    seq_pb = [x for x in seq if x != "T"]
    if len(seq_pb) == 0:
        st.info("Ainda não há P/B suficientes para leitura.")
    else:
        ult_pb = seq_pb[-12:]  # janela de leitura curta

        # DOMINÂNCIA DE COR
        cont = Counter(ult_pb)
        total_v = sum(cont.values())
        dom_p = cont.get("P", 0) / total_v if total_v else 0
        dom_b = cont.get("B", 0) / total_v if total_v else 0

        # STREAK (3+ e 4+)
        streak_side = None
        streak_len = 1
        if len(ult_pb) >= 2:
            last = ult_pb[-1]
            streak_len = 1
            for x in reversed(ult_pb[:-1]):
                if x == last:
                    streak_len += 1
                else:
                    break
            if streak_len >= 3:
                streak_side = last  # 'P' ou 'B'

        # ZIGZAG / CHOP
        zigzag = False
        if len(ult_pb) >= 6:
            diffs = sum(1 for i in range(len(ult_pb)-1) if ult_pb[i] != ult_pb[i+1])
            if diffs >= len(ult_pb) - 2:
                zigzag = True

        # BLOCK 2–2 / 3–3 (foco 2–2)
        block_side = None
        if len(ult_pb) >= 4:
            ult4 = ult_pb[-4:]
            if ult4[:2] == ult4[2:] and ult4[0] != ult4[2]:
                # PPBB ou BBPP
                block_side = ult4[-1]

        # TIE ZONE (empates recentes)
        ult9 = seq[-9:] if len(seq) >= 9 else seq
        ties_9 = ult9.count("T")
        tie_zone = ties_9 >= 2

        # ESTADO DA MESA
        if streak_side and streak_len >= 4:
            estado = f"STREAK FORTE {'PLAYER' if streak_side=='P' else 'BANKER'} ({streak_len})"
            tendencia = streak_side
        elif streak_side:
            estado = f"STREAK {'PLAYER' if streak_side=='P' else 'BANKER'} ({streak_len})"
            tendencia = streak_side
        elif zigzag:
            estado = "ZIGZAG (Chop forte)"
            tendencia = None
        elif block_side:
            estado = f"BLOCK {'PLAYER' if block_side=='P' else 'BANKER'}"
            tendencia = block_side
        elif dom_p >= 0.6:
            estado = "Tendência PLAYER"
            tendencia = "P"
        elif dom_b >= 0.6:
            estado = "Tendência BANKER"
            tendencia = "B"
        else:
            estado = "Neutro/Compressão"
            tendencia = None

        # SUGESTÃO OPERACIONAL
        if tie_zone and not tendencia:
            tipo = "TIE"
            sugestao = "Zona de TIE: considerar T apenas com stake mínima."
        elif estado.startswith("STREAK FORTE"):
            lado = "PLAYER" if tendencia == "P" else "BANKER"
            tipo = "P/B"
            sugestao = f"STREAK forte: seguir {lado} com stake maior até sinal de quebra."
        elif estado.startswith("STREAK"):
            lado = "PLAYER" if tendencia == "P" else "BANKER"
            tipo = "P/B"
            sugestao = f"STREAK ativo: seguir {lado} com stake leve."
        elif estado.startswith("BLOCK"):
            lado = "PLAYER" if tendencia == "P" else "BANKER"
            tipo = "P/B"
            sugestao = f"BLOCK formado: operar a favor de {lado} na continuidade do bloco."
        elif estado.startswith("Tendência"):
            lado = "PLAYER" if tendencia == "P" else "BANKER"
            tipo = "P/B"
            sugestao = f"Tendência de cor: entrada moderada em {lado}."
        elif zigzag:
            tipo = "ZIGZAG"
            sugestao = "ZIGZAG forte: evitar entradas pesadas; se operar, usar mão mínima."
        else:
            tipo = "NEUTRO"
            sugestao = "Sem padrão confiável: melhor aguardar formação."

        # EXIBIÇÃO
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Dom. Player", f"{dom_p*100:.1f}%")
        with c2:
            st.metric("Dom. Banker", f"{dom_b*100:.1f}%")
        with c3:
            st.metric("Estado da mesa", estado)

        st.subheader("🎯 Leitura / Sugestão")
        if tipo in ["P/B", "TIE"]:
            st.success(sugestao)
        elif tipo == "ZIGZAG":
            st.warning(sugestao)
        else:
            st.info(sugestao)

else:
    st.info("Registre pelo menos 6 rodadas para começar a leitura profissional.")
