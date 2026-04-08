"""
EvoLLM — Interfaz Gráfica
Simulador evolutivo del Dilema del Prisionero con estrategias de LLM
"""

import ast
import io
import os
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
RESULTS_DIR = PROJECT_ROOT / "results"
STRATEGIES_DIR = PROJECT_ROOT / "strategies"
SRC_MORAN = PROJECT_ROOT / "src" / "evollm" / "moran_process.py"
SRC_H2H = PROJECT_ROOT / "src" / "evollm" / "head_to_head.py"

STRATEGY_MODULES = sorted([p.stem for p in STRATEGIES_DIR.glob("*.py")])

ATTITUDE_LABELS = {
    "Aggressive": "Agresivo",
    "Cooperative": "Cooperativo",
    "Neutral": "Neutral",
}

ATTITUDE_COLORS = {
    "Aggressive": "#EF553B",
    "Cooperative": "#00CC96",
    "Neutral": "#636EFA",
    "Agresivo": "#EF553B",
    "Cooperativo": "#00CC96",
    "Neutral ": "#636EFA",
}

MODULE_LABELS = {
    "anthropic_default": "Anthropic — Prompt directo",
    "anthropic_default_noise": "Anthropic — Directo + ruido",
    "anthropic_prose": "Anthropic — Escenario prosa",
    "anthropic_prose_noise": "Anthropic — Prosa + ruido",
    "anthropic_refine": "Anthropic — Refinado",
    "anthropic_refine_noise": "Anthropic — Refinado + ruido",
    "openai_default": "OpenAI — Prompt directo",
    "openai_default_noise": "OpenAI — Directo + ruido",
    "openai_prose": "OpenAI — Escenario prosa",
    "openai_prose_noise": "OpenAI — Prosa + ruido",
    "openai_refine": "OpenAI — Refinado",
    "openai_refine_noise": "OpenAI — Refinado + ruido",
}

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EvoLLM — Simulador del Dilema del Prisionero",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  .log-box {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 12px;
    border-radius: 6px;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.4;
  }
  .metric-label { font-size: 13px; color: #888; }
  .metric-value { font-size: 28px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------
st.session_state.setdefault("moran_winner_counts", {})
st.session_state.setdefault("moran_last_algo", "")
st.session_state.setdefault("moran_plot_ready", False)
st.session_state.setdefault("torneo_last_algo", "")
st.session_state.setdefault("torneo_last_mode", "")


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def get_subprocess_env():
    """Entorno con PYTHONPATH apuntando a src/."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return env


def run_subprocess_streaming(cmd: list[str]):
    """
    Ejecuta un comando y hace yield de cada línea de salida.
    Retorna el código de salida al final como un string especial '__returncode__:{code}'.
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=get_subprocess_env(),
        cwd=str(PROJECT_ROOT),
    )
    for line in proc.stdout:
        yield line.rstrip()
    proc.wait()
    yield f"__returncode__:{proc.returncode}"


def parse_winner_counts(output_lines: list[str]) -> dict:
    """Extrae el dict de ganadores de la salida de moran_process.py."""
    for line in reversed(output_lines):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return ast.literal_eval(line)
            except Exception:
                pass
    return {}


def parse_matrices_txt(filepath: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Parsea un archivo *_matrices.txt y retorna:
    (cooperation_df, payoffs_df, summary_df)
    """
    text = filepath.read_text(encoding="utf-8")
    sections = {}

    markers = ["Normalised cooperation:", "Payoffs:", "Results Summary:"]
    positions = []
    for m in markers:
        idx = text.find(m)
        if idx != -1:
            positions.append((idx, m))
    positions.sort()

    for i, (pos, marker) in enumerate(positions):
        start = pos + len(marker)
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        sections[marker] = text[start:end].strip()

    def read_df(key):
        raw = sections.get(key, "")
        if not raw:
            return pd.DataFrame()
        try:
            return pd.read_csv(io.StringIO(raw), sep=r"\s{2,}", engine="python", index_col=0)
        except Exception:
            return pd.DataFrame()

    cooperation_df = read_df("Normalised cooperation:")
    payoffs_df = read_df("Payoffs:")

    summary_raw = sections.get("Results Summary:", "")
    try:
        summary_df = pd.read_csv(io.StringIO(summary_raw), sep=r"\s{2,}", engine="python")
    except Exception:
        summary_df = pd.DataFrame()

    return cooperation_df, payoffs_df, summary_df


def make_heatmap(df: pd.DataFrame, title: str, colorscale: str = "RdYlGn", fmt: str = ".3f") -> go.Figure:
    """Retorna figura Plotly de heatmap con anotaciones numéricas."""
    if df.empty:
        return go.Figure()

    cols = [ATTITUDE_LABELS.get(c, c) for c in df.columns]
    rows = [ATTITUDE_LABELS.get(r, r) for r in df.index]
    values = df.values

    annotations = []
    for i, row in enumerate(rows):
        for j, col in enumerate(cols):
            annotations.append(dict(
                x=col, y=row,
                text=format(values[i, j], fmt),
                showarrow=False,
                font=dict(color="black", size=14),
            ))

    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=cols,
        y=rows,
        colorscale=colorscale,
        zmin=0 if "RdYlGn" in colorscale else None,
        zmax=1 if "RdYlGn" in colorscale else None,
        showscale=True,
    ))
    fig.update_layout(
        title=title,
        annotations=annotations,
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(size=13),
    )
    return fig


def make_winner_bar(winner_counts: dict) -> go.Figure:
    """Gráfica de barras con distribución de ganadores del Proceso de Moran."""
    if not winner_counts:
        return go.Figure()

    labels = []
    values = []
    colors = []
    for name, count in sorted(winner_counts.items(), key=lambda x: -x[1]):
        label = ATTITUDE_LABELS.get(name, name)
        labels.append(label)
        values.append(count)
        colors.append(ATTITUDE_COLORS.get(name, ATTITUDE_COLORS.get(label, "#636EFA")))

    total = sum(values)
    fig = px.bar(
        x=labels,
        y=values,
        color=labels,
        color_discrete_map={ATTITUDE_LABELS.get(k, k): v for k, v in ATTITUDE_COLORS.items()},
        text=[f"{v} ({100*v/total:.1f}%)" for v in values],
        labels={"x": "Actitud ganadora", "y": "Número de veces ganada"},
        title="Distribución de ganadores",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def list_available_experiments() -> list[str]:
    """Lista los módulos para los que existe un archivo _matrices.txt en results/."""
    if not RESULTS_DIR.exists():
        return []
    files = sorted(RESULTS_DIR.glob("*_matrices.txt"))
    names = []
    for f in files:
        stem = f.stem.replace("_matrices", "")
        names.append(stem)
    return names


def module_display_name(module: str) -> str:
    return MODULE_LABELS.get(module, module)


# ---------------------------------------------------------------------------
# Encabezado principal
# ---------------------------------------------------------------------------
st.title("🧬 EvoLLM — Simulador del Dilema del Prisionero")
st.caption(
    "Herramienta de investigación: simulación evolutiva de estrategias generadas por LLMs "
    "en juegos de dilema social (Proceso de Moran)."
)

tab_moran, tab_torneo, tab_dashboard = st.tabs([
    "🔁  Simulación Moran",
    "⚔️  Torneo",
    "📊  Dashboard de Resultados",
])


# ===========================================================================
# PESTAÑA 1: SIMULACIÓN MORAN
# ===========================================================================
with tab_moran:
    st.header("Proceso de Moran — Simulación Evolutiva")
    st.markdown(
        """
        El **Proceso de Moran** simula cómo una población de jugadores evoluciona a lo largo
        del tiempo. En cada paso, el jugador con mayor puntaje se "reproduce" y otro muere,
        hasta que una sola estrategia domina la población (**fijación**).

        Puedes correr cientos de iteraciones para estimar qué actitud (Agresiva, Cooperativa o
        Neutral) tiende a ganar con más frecuencia.
        """
    )

    with st.form("moran_form"):
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("Estrategias y simulación")
            algo_sel = st.selectbox(
                "Módulo de estrategias",
                STRATEGY_MODULES,
                format_func=module_display_name,
                help="Elige el conjunto de estrategias LLM a usar en la simulación.",
            )

            iteraciones = st.slider(
                "Número de iteraciones",
                min_value=10, max_value=500, value=100, step=10,
                help="Cuántas veces se repite la simulación completa. Más iteraciones = resultados más estables.",
            )

            procesos = st.slider(
                "Procesos paralelos",
                min_value=1, max_value=8, value=1,
                help="Usar más procesos acelera la simulación si tu computadora tiene varios núcleos.",
            )

            modo_trayectoria = st.checkbox(
                "Mostrar trayectoria individual (una sola ejecución con gráfico)",
                value=False,
                help="Activa para ver cómo evoluciona la población paso a paso en una sola ejecución.",
            )

        with col_right:
            st.subheader("Población inicial")
            st.caption("Define cuántos jugadores de cada actitud inician la simulación.")

            n_agresivos = st.number_input("Jugadores Agresivos", min_value=1, max_value=20, value=4)
            n_cooperativos = st.number_input("Jugadores Cooperativos", min_value=1, max_value=20, value=4)
            n_neutrales = st.number_input("Jugadores Neutrales", min_value=1, max_value=20, value=4)

            st.markdown("---")
            st.subheader("Filtro de estrategias")
            st.caption("Permite usar solo las estrategias mejor o peor clasificadas.")

            keep_top = st.slider(
                "keep_top (0 = las mejores, 0.5 = top 50%)",
                min_value=0.0, max_value=0.9, value=0.0, step=0.05,
            )
            keep_bottom = st.slider(
                "keep_bottom (1 = todas, 0.5 = bottom 50%)",
                min_value=0.1, max_value=1.0, value=1.0, step=0.05,
            )

        ejecutar_moran = st.form_submit_button("▶  Ejecutar simulación", use_container_width=True)

    if ejecutar_moran:
        if keep_top >= keep_bottom:
            st.error("⚠️ keep_top debe ser menor que keep_bottom.")
        else:
            algo_path = str(STRATEGIES_DIR / algo_sel)
            cmd = [
                sys.executable, str(SRC_MORAN),
                "--algo", algo_path,
                "--initial_pop", str(n_agresivos), str(n_cooperativos), str(n_neutrales),
                "--keep_top", str(keep_top),
                "--keep_bottom", str(keep_bottom),
            ]
            if modo_trayectoria:
                cmd.append("--plot")
            else:
                cmd += ["--iterations", str(iteraciones), "--processes", str(procesos)]

            st.markdown("**Registro de ejecución:**")
            log_placeholder = st.empty()
            output_lines = []
            returncode = 0

            with st.spinner("Simulando..."):
                log_text = ""
                for line in run_subprocess_streaming(cmd):
                    if line.startswith("__returncode__:"):
                        returncode = int(line.split(":")[1])
                    else:
                        output_lines.append(line)
                        log_text += line + "\n"
                        log_placeholder.markdown(
                            f'<div class="log-box">{log_text[-3000:]}</div>',
                            unsafe_allow_html=True,
                        )

            if returncode != 0:
                st.error(f"La simulación terminó con error (código {returncode}). Revisa el log.")
            else:
                st.success("✅ Simulación completada.")

                if modo_trayectoria:
                    moran_img = RESULTS_DIR / "example_moran.png"
                    if moran_img.exists():
                        st.subheader("Trayectoria de población")
                        st.caption(
                            "Cada área de color representa una actitud. "
                            "El eje X muestra los pasos del proceso y el Y el número de jugadores."
                        )
                        st.image(str(moran_img), use_container_width=False, width=600)
                else:
                    winner_counts = parse_winner_counts(output_lines)
                    if winner_counts:
                        st.session_state["moran_winner_counts"] = winner_counts
                        st.session_state["moran_last_algo"] = algo_sel

                        st.subheader("Resultados — Distribución de ganadores")
                        total = sum(winner_counts.values())
                        cols_met = st.columns(len(winner_counts))
                        for i, (name, count) in enumerate(
                            sorted(winner_counts.items(), key=lambda x: -x[1])
                        ):
                            label = ATTITUDE_LABELS.get(name, name)
                            with cols_met[i]:
                                st.metric(
                                    label=label,
                                    value=f"{count} veces",
                                    delta=f"{100 * count / total:.1f}%",
                                )

                        st.plotly_chart(
                            make_winner_bar(winner_counts),
                            use_container_width=True,
                            key="moran_winner_bar",
                        )
                    else:
                        st.warning("No se pudo extraer el conteo de ganadores del log.")


# ===========================================================================
# PESTAÑA 2: TORNEO
# ===========================================================================
with tab_torneo:
    st.header("Análisis de Torneo")
    st.markdown(
        """
        Compara estrategias LLM mediante torneos:

        - **Beaufils**: Las estrategias LLM se enfrentan a 10 estrategias clásicas
          (Cooperador, Traidor, TitForTat, Rencoroso, etc.). Muestra qué tan bien
          compiten contra jugadores conocidos de la literatura.

        - **Head-to-head**: Las estrategias LLM se enfrentan entre sí.
          Genera matrices de cooperación y pagos por actitud, y una tabla de clasificación.
        """
    )

    with st.form("torneo_form"):
        col_t1, col_t2 = st.columns([1, 1])

        with col_t1:
            algo_t = st.selectbox(
                "Módulo de estrategias",
                STRATEGY_MODULES,
                format_func=module_display_name,
            )
            modo_torneo = st.radio(
                "Tipo de torneo",
                ["Beaufils (LLM vs estrategias clásicas)", "Head-to-head (LLM vs LLM)"],
            )

        with col_t2:
            st.subheader("Filtro de estrategias")
            keep_top_t = st.slider(
                "keep_top", min_value=0.0, max_value=0.9, value=0.0, step=0.05, key="t_kt"
            )
            keep_bottom_t = st.slider(
                "keep_bottom", min_value=0.1, max_value=1.0, value=1.0, step=0.05, key="t_kb"
            )

        ejecutar_torneo = st.form_submit_button("▶  Ejecutar torneo", use_container_width=True)

    if ejecutar_torneo:
        if keep_top_t >= keep_bottom_t:
            st.error("⚠️ keep_top debe ser menor que keep_bottom.")
        else:
            algo_t_path = str(STRATEGIES_DIR / algo_t)
            cmd_t = [
                sys.executable, str(SRC_H2H),
                "--algo", algo_t_path,
                "--keep_top", str(keep_top_t),
                "--keep_bottom", str(keep_bottom_t),
            ]
            if "Head-to-head" in modo_torneo:
                cmd_t.append("--h2h")

            st.markdown("**Registro de ejecución:**")
            log_ph_t = st.empty()
            out_lines_t = []
            rc_t = 0

            with st.spinner("Ejecutando torneo (puede tardar varios minutos)..."):
                log_t = ""
                for line in run_subprocess_streaming(cmd_t):
                    if line.startswith("__returncode__:"):
                        rc_t = int(line.split(":")[1])
                    else:
                        out_lines_t.append(line)
                        log_t += line + "\n"
                        log_ph_t.markdown(
                            f'<div class="log-box">{log_t[-3000:]}</div>',
                            unsafe_allow_html=True,
                        )

            if rc_t != 0:
                st.error(f"El torneo terminó con error (código {rc_t}).")
            else:
                st.success("✅ Torneo completado.")
                st.session_state["torneo_last_algo"] = algo_t
                st.session_state["torneo_last_mode"] = modo_torneo

                if "Beaufils" in modo_torneo:
                    beaufils_svg = RESULTS_DIR / "beaufils.svg"
                    if beaufils_svg.exists():
                        st.subheader("Resultados Beaufils")
                        st.caption(
                            "Cada caja muestra la distribución de puntajes de una estrategia "
                            "a lo largo de 200 repeticiones del torneo."
                        )
                        st.image(str(beaufils_svg), use_container_width=True)
                    else:
                        st.warning("No se encontró el archivo beaufils.svg en results/.")

                else:
                    matrices_file = RESULTS_DIR / f"{algo_t}_matrices.txt"
                    if matrices_file.exists():
                        coop_df, pay_df, sum_df = parse_matrices_txt(matrices_file)

                        st.subheader("Matrices de interacción")
                        col_h1, col_h2 = st.columns(2)
                        with col_h1:
                            st.plotly_chart(
                                make_heatmap(
                                    coop_df,
                                    "Tasa de Cooperación (0=traición, 1=cooperación total)",
                                    "RdYlGn",
                                    ".3f",
                                ),
                                use_container_width=True,
                                key="torneo_h2h_coop",
                            )
                            st.caption(
                                "Verde = alta cooperación, Rojo = alta traición. "
                                "Las filas indican el jugador, las columnas el oponente."
                            )
                        with col_h2:
                            st.plotly_chart(
                                make_heatmap(pay_df, "Pagos medios por actitud", "Blues", ".2f"),
                                use_container_width=True,
                                key="torneo_h2h_pay",
                            )
                            st.caption("Puntaje promedio obtenido por cada actitud frente a cada oponente.")

                        if not sum_df.empty:
                            st.subheader("Tabla de clasificación")
                            st.dataframe(sum_df, use_container_width=True, height=400)
                    else:
                        st.warning(f"No se encontró {matrices_file.name} en results/.")


# ===========================================================================
# PESTAÑA 3: DASHBOARD DE RESULTADOS
# ===========================================================================
with tab_dashboard:
    st.header("Dashboard de Resultados")
    st.markdown(
        "Explora los resultados de experimentos ya ejecutados. "
        "Selecciona un experimento o compara varios entre sí."
    )

    available = list_available_experiments()

    if not available:
        st.info(
            "No hay resultados disponibles aún. "
            "Ejecuta un torneo Head-to-head en la pestaña ⚔️ Torneo para generar datos."
        )
    else:
        # --- Selector de experimento ---
        exp_sel = st.selectbox(
            "Experimento",
            available,
            format_func=module_display_name,
        )

        matrices_path = RESULTS_DIR / f"{exp_sel}_matrices.txt"
        coop_df, pay_df, sum_df = parse_matrices_txt(matrices_path)

        # --- Sección de métricas rápidas ---
        if not sum_df.empty:
            name_col = "Name" if "Name" in sum_df.columns else sum_df.columns[0]
            score_col = "Median_score" if "Median_score" in sum_df.columns else None
            coop_col = "Cooperation_rating" if "Cooperation_rating" in sum_df.columns else None

            st.subheader("Métricas generales")
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                st.metric("Total de estrategias", len(sum_df))
            if score_col:
                with mc2:
                    best_row = sum_df.loc[sum_df[score_col].idxmax()]
                    best_name = best_row.get(name_col, "?")
                    st.metric("Mejor puntaje", f"{sum_df[score_col].max():.3f}", delta=best_name)
                with mc3:
                    st.metric("Puntaje promedio", f"{sum_df[score_col].mean():.3f}")
            if coop_col:
                with mc4:
                    st.metric("Cooperación media", f"{sum_df[coop_col].mean():.3f}")

        st.markdown("---")

        # --- Heatmaps ---
        st.subheader("Matrices de interacción entre actitudes")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            fig_coop = make_heatmap(
                coop_df,
                "Tasa de Cooperación normalizada",
                "RdYlGn", ".3f",
            )
            st.plotly_chart(fig_coop, use_container_width=True, key="dash_coop")
            st.caption(
                "Verde oscuro = cooperación casi total. Rojo = traición. "
                "Por ejemplo, Cooperativo vs Cooperativo suele estar cerca de 1.0."
            )

        with col_d2:
            fig_pay = make_heatmap(pay_df, "Pagos medios por actitud", "Blues", ".2f")
            st.plotly_chart(fig_pay, use_container_width=True, key="dash_pay")
            st.caption(
                "Puntaje promedio obtenido en cada combinación de actitudes. "
                "Los valores más altos indican mayor éxito en el juego."
            )

        # --- Radar de actitudes ---
        if not coop_df.empty:
            st.subheader("Perfil de cooperación por actitud (radar)")
            attitudes_orig = list(coop_df.index)
            categories = [ATTITUDE_LABELS.get(a, a) for a in coop_df.columns]

            fig_radar = go.Figure()
            colors_radar = ["#EF553B", "#00CC96", "#636EFA"]
            for i, att in enumerate(attitudes_orig):
                vals = coop_df.loc[att].tolist()
                vals_closed = vals + [vals[0]]
                cats_closed = categories + [categories[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals_closed,
                    theta=cats_closed,
                    fill="toself",
                    name=ATTITUDE_LABELS.get(att, att),
                    line_color=colors_radar[i % len(colors_radar)],
                    opacity=0.7,
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(range=[0, 1], tickfont_size=10)),
                height=350,
                margin=dict(l=40, r=40, t=40, b=40),
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(fig_radar, use_container_width=False, key="dash_radar")
            st.caption(
                "Cada eje representa un tipo de oponente. "
                "Una actitud que ocupa más área coopera más en general."
            )

        # --- Gráfica de ganadores de la sesión actual ---
        if st.session_state.get("moran_winner_counts"):
            st.markdown("---")
            st.subheader("Distribución de ganadores (última simulación Moran)")
            last_algo = st.session_state.get("moran_last_algo", "")
            if last_algo:
                st.caption(f"Módulo: **{module_display_name(last_algo)}**")
            st.plotly_chart(
                make_winner_bar(st.session_state["moran_winner_counts"]),
                use_container_width=True,
                key="dash_winner_bar",
            )

        # --- Imagen Moran (si existe) ---
        moran_img_path = RESULTS_DIR / "example_moran.png"
        exp_img_path = RESULTS_DIR / f"{exp_sel}.png"
        img_to_show = exp_img_path if exp_img_path.exists() else (
            moran_img_path if moran_img_path.exists() else None
        )
        if img_to_show:
            st.markdown("---")
            st.subheader("Trayectoria de población (Proceso de Moran)")
            st.image(str(img_to_show), width=600)
            st.caption(
                "El eje X muestra los pasos del proceso evolutivo. "
                "El eje Y muestra cuántos jugadores de cada actitud hay en la población. "
                "La simulación termina cuando una sola actitud domina completamente."
            )

        # --- Tabla de clasificación ---
        if not sum_df.empty:
            st.markdown("---")
            st.subheader("Tabla de clasificación completa")

            name_col = "Name" if "Name" in sum_df.columns else sum_df.columns[0]

            # Filtros
            fc1, fc2 = st.columns([1, 2])
            with fc1:
                att_filter = st.multiselect(
                    "Filtrar por actitud",
                    ["Aggressive", "Cooperative", "Neutral"],
                    default=["Aggressive", "Cooperative", "Neutral"],
                    format_func=lambda x: ATTITUDE_LABELS.get(x, x),
                )
            with fc2:
                if score_col and score_col in sum_df.columns:
                    min_score = float(sum_df[score_col].min())
                    max_score = float(sum_df[score_col].max())
                    score_range = st.slider(
                        "Rango de puntaje",
                        min_value=min_score,
                        max_value=max_score,
                        value=(min_score, max_score),
                        step=0.01,
                    )

            filtered_df = sum_df.copy()
            if name_col in filtered_df.columns and att_filter:
                mask = filtered_df[name_col].str.contains("|".join(att_filter), na=False)
                filtered_df = filtered_df[mask]
            if score_col and score_col in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df[score_col] >= score_range[0]) &
                    (filtered_df[score_col] <= score_range[1])
                ]

            st.dataframe(filtered_df, use_container_width=True, height=450)

            # Botón de descarga
            csv_bytes = filtered_df.to_csv(index=True).encode("utf-8")
            st.download_button(
                label="⬇ Descargar tabla como CSV",
                data=csv_bytes,
                file_name=f"{exp_sel}_clasificacion.csv",
                mime="text/csv",
            )

        # --- Comparación entre experimentos ---
        st.markdown("---")
        st.subheader("Comparación entre experimentos")
        st.caption("Selecciona 2 o más experimentos para comparar el puntaje mediano por actitud.")

        compare_sel = st.multiselect(
            "Experimentos a comparar",
            available,
            default=available[:2] if len(available) >= 2 else available,
            format_func=module_display_name,
        )

        if len(compare_sel) >= 2:
            compare_rows = []
            for exp in compare_sel:
                mpath = RESULTS_DIR / f"{exp}_matrices.txt"
                _, _, sdf = parse_matrices_txt(mpath)
                if sdf.empty:
                    continue
                name_c = "Name" if "Name" in sdf.columns else sdf.columns[0]
                score_c = "Median_score" if "Median_score" in sdf.columns else None
                if not score_c:
                    continue
                for att in ["Aggressive", "Cooperative", "Neutral"]:
                    subset = sdf[sdf[name_c].str.startswith(att)]
                    if not subset.empty:
                        compare_rows.append({
                            "Experimento": module_display_name(exp),
                            "Actitud": ATTITUDE_LABELS.get(att, att),
                            "Puntaje mediano": subset[score_c].median(),
                        })

            if compare_rows:
                compare_df = pd.DataFrame(compare_rows)
                fig_cmp = px.bar(
                    compare_df,
                    x="Experimento",
                    y="Puntaje mediano",
                    color="Actitud",
                    barmode="group",
                    color_discrete_map={
                        "Agresivo": "#EF553B",
                        "Cooperativo": "#00CC96",
                        "Neutral": "#636EFA",
                    },
                    title="Puntaje mediano por actitud y experimento",
                )
                fig_cmp.update_layout(
                    height=400,
                    xaxis_tickangle=-25,
                    margin=dict(l=10, r=10, t=50, b=80),
                )
                st.plotly_chart(fig_cmp, use_container_width=True, key="dash_compare")
            else:
                st.info("No hay datos suficientes para comparar los experimentos seleccionados.")
        elif len(compare_sel) == 1:
            st.info("Selecciona al menos 2 experimentos para comparar.")
