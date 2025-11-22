import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# Configuración de directorios
RESULTS_BASE_DIR = Path("results")
ANALYSIS_BASE_DIR = Path("analysis")

# Configuración de Plotly
pio.templates.default = "plotly_white"

def get_analysis_paths():
    folder_name = input("Introduce el nombre de la carpeta del experimento a analizar: ").strip()
    input_dir = RESULTS_BASE_DIR / folder_name
    output_dir = ANALYSIS_BASE_DIR / folder_name

    if not input_dir.exists():
        print(f"❌ Error: El directorio de resultados '{input_dir}' no existe.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    return input_dir, output_dir

def save_excel(df: pd.DataFrame, path: Path, sheet_name="Sheet1"):
    """Helper para guardar en Excel de forma consistente"""
    try:
        # Aseguramos que la extensión sea .xlsx
        save_path = path.with_suffix(".xlsx")
        df.to_excel(save_path, index=False, sheet_name=sheet_name)
        print(f"💾 Excel guardado: {save_path.name}")
    except Exception as e:
        print(f"⚠️ Error guardando Excel {path.name}: {e}")

def load_data(input_dir: Path):
    ranking_path = input_dir / "ranking_data.csv"
    h2h_path = input_dir / "head_to_head_data.csv"
    try:
        ranking_df = pd.read_csv(ranking_path)
        h2h_df = pd.read_csv(h2h_path)
        
        # --- LÓGICA DE NORMALIZACIÓN (Senior Refactor) ---
        # Centralizamos aquí el cálculo para que todo el script use la métrica limpia.
        
        col_generations = "n_generations"
        
        # Validación defensiva: Si el usuario olvidó guardar n_generations en el CSV anterior
        if col_generations not in ranking_df.columns:
            print(f"⚠️ ADVERTENCIA: La columna '{col_generations}' no está en el CSV.")
            print("   -> Se asumirá valor 1.0 para evitar errores, pero el reward NO estará normalizado.")
            ranking_df[col_generations] = 1.0
        
        # Creación de la métrica 'normalized_reward':
        #( (reward / n_generations) / n_repetitions) /(n_jugadores - 1)
        # Esto lo hacemos para que podamos lograr una metrica de reward representativa de un match: ignorando el numero de generaciones que ha durado la evolucion
        # y el numero de veces que se ha repetido un match. También lo hacemos agnostico al numero de enfrentamiento que haya tenido que hacer un agente
        n_players = len(set(ranking_df["agent_name"]))
        ranking_df["normalized_reward"] = ((ranking_df["reward"] / ranking_df[col_generations]) / ranking_df["n_repetitions"]) / (n_players - 1)
        print(ranking_df)
        
        print(f"✅ Datos cargados y normalizados: {len(ranking_df)} registros.")
        return ranking_df, h2h_df
    except Exception as e:
        print(f"❌ Error crítico cargando datos: {e}")
        sys.exit(1)

# =============================================================================
# BLOQUE 1: ANÁLISIS DE EVOLUCIÓN (RANKING DATA)
# =============================================================================

def plot_reward_vs_error(df: pd.DataFrame, output_dir: Path):
    """Plot 1: Reward Normalizado Medio vs Probabilidad de Error"""
    # Usamos normalized_reward
    ranking_mean = df.groupby(["agent_name", "error_prob"])["normalized_reward"].median().reset_index()
    
    fig = go.Figure()
    for agent_name, group in ranking_mean.groupby("agent_name"):
        group = group.sort_values("error_prob")
        fig.add_trace(go.Scatter(
            x=group["error_prob"], y=group["normalized_reward"],
            mode="lines+markers", name=str(agent_name),
            hovertemplate="<b>%{text}</b><br>Error: %{x}<br>Norm. Reward: %{y:.4f}<extra></extra>",
            text=[agent_name] * len(group)
        ))

    fig.update_layout(
        title="Reward Normalizado (por Generación) vs Probabilidad de Error",
        xaxis_title="Error Probability", yaxis_title="Mean Normalized Reward",
        hovermode="x unified"
    )
    pio.write_html(fig, file=output_dir / "reward_vs_error_prob.html", auto_open=False)
    print("📊 Plot generado: reward_vs_error_prob.html")

def plot_reward_vs_repetitions(df: pd.DataFrame, output_dir: Path):
    """Plot 2: Reward Normalizado Medio vs Número de Repeticiones"""
    ranking_mean = df.groupby(["agent_name", "n_repetitions"])["normalized_reward"].median().reset_index()

    fig = go.Figure()
    for agent_name, group in ranking_mean.groupby("agent_name"):
        group = group.sort_values("n_repetitions")
        fig.add_trace(go.Scatter(
            x=group["n_repetitions"], y=group["normalized_reward"],
            mode="lines+markers", name=str(agent_name)
        ))

    fig.update_layout(
        title="Reward Normalizado vs Número de Repeticiones",
        xaxis_title="Número de Repeticiones", yaxis_title="Mean Normalized Reward",
        hovermode="x unified"
    )
    pio.write_html(fig, file=output_dir / "reward_vs_repetitions.html", auto_open=False)
    print("📊 Plot generado: reward_vs_repetitions.html")

def plot_reward_derivative(df: pd.DataFrame, output_dir: Path):
    """Plot 3: Velocidad de mejora del Reward Normalizado"""
    ranking_mean = df.groupby(["agent_name", "n_repetitions"])["normalized_reward"].median().reset_index()
    
    fig = go.Figure()
    derivative_data = []

    for agent_name, group in ranking_mean.groupby("agent_name"):
        group = group.sort_values("n_repetitions")
        if len(group) < 2:
            continue

        d_reward = np.diff(group["normalized_reward"])
        d_n = np.diff(group["n_repetitions"])
        
        with np.errstate(divide='ignore', invalid='ignore'):
            derivative = np.where(d_n != 0, d_reward / d_n, 0)
            
        n_midpoints = group["n_repetitions"].values[:-1] + d_n / 2
        
        fig.add_trace(go.Scatter(
            x=n_midpoints, y=derivative,
            mode="lines+markers", name=str(agent_name)
        ))
        
        for nm, der in zip(n_midpoints, derivative):
            derivative_data.append({'agent': agent_name, 'n_mid': nm, 'derivative': der})

    fig.update_layout(
        title="Velocidad de Mejora (dNormReward/dN)",
        xaxis_title="N Repetitions (Midpoint)", yaxis_title="Rate of Change (Normalized)",
        hovermode="x unified"
    )
    pio.write_html(fig, file=output_dir / "reward_derivative.html", auto_open=False)
    
    if derivative_data:
        # Guardar datos de derivadas en Excel
        save_excel(pd.DataFrame(derivative_data), output_dir / "derivative_data")
    
    print("📊 Plot y datos guardados: reward_derivative")

def analyze_top_performers(df: pd.DataFrame, output_dir: Path):
    """Genera XLSX y TXT con los Top 3 modelos (Basado en Reward Normalizado)"""
    
    # Agrupamos y calculamos estadísticas sobre normalized_reward
    grouped = (
        df.groupby(["error_prob", "n_repetitions", "agent_name"])["normalized_reward"]
        .agg(["mean", "std", "min", "max", "median"])
        .reset_index()
    )

    def get_top5(sub_df):
        return sub_df.sort_values("mean", ascending=False).head(5)

    best_models = grouped.groupby(["error_prob", "n_repetitions"], group_keys=False).apply(get_top5)
    
    # 1. Guardar Excel (Cambio solicitado)
    save_excel(best_models, output_dir / "best_models_per_tournament")
    
    # 2. Guardar Reporte de Texto
    txt_path = output_dir / "best_models_report.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=== TOP 3 MODELS (NORMALIZED REWARD) ===\n\n")
        for (err, reps), subdf in best_models.groupby(["error_prob", "n_repetitions"]):
            header = f"Tournament [Error: {err:.2f} | Reps: {reps}]"
            f.write(f"{header}\n" + "="*len(header) + "\n")
            for _, row in subdf.iterrows():
                f.write(f"   - {row['agent_name']:<15} | Mean Norm. Reward: {row['mean']:.4f} (std: {row['std']:.4f})\n")
            f.write("\n")
            
    print(f"📄 Reporte Top-3 generado.")

# =============================================================================
# BLOQUE 2: ANÁLISIS HEAD-TO-HEAD
# =============================================================================

def analyze_win_rates_and_stats(h2h_df: pd.DataFrame,ranking_df:pd.DataFrame ,  output_dir: Path):
    """Calcula Win Rates y Estadísticas. Guarda en XLSX."""
    
    # 1. Win Rates Globales
    total_wins = h2h_df["winner"].value_counts()
    all_participations = pd.concat([h2h_df["agent_A"], h2h_df["agent_B"]])
    total_matches = all_participations.value_counts()
    
    win_rate = (total_wins / total_matches).fillna(0).sort_values(ascending=False)
    win_rate_df = win_rate.reset_index()
    win_rate_df.columns = ["agent_name", "win_rate"]
    
    save_excel(win_rate_df, output_dir / "global_win_rates")
    
    # 2. Estadísticas de Reward 
    stats = ranking_df.groupby("agent_name")["normalized_reward"].agg(["mean" ,"std", "min","median", "max"]).sort_values("median", ascending=False).reset_index()
    save_excel(stats, output_dir / "global_reward_stats")
    
    print("✅ Estadísticas globales (Win Rates y Rewards) guardadas en Excel.")

def plot_head_to_head_matrix(h2h_df: pd.DataFrame, output_dir: Path):
    """Genera Matriz de Heatmap y guarda CSV/Excel de la matriz"""
    
    conditions = [
        h2h_df["winner"] == h2h_df["agent_A"],
        h2h_df["winner"] == h2h_df["agent_B"]
    ]
    choices = [h2h_df["agent_B"], h2h_df["agent_A"]]
    h2h_df["loser"] = np.select(conditions, choices, default=None)

    wins_matrix = pd.crosstab(h2h_df["winner"], h2h_df["loser"])
    all_agents = sorted(list(set(h2h_df["agent_A"].unique()) | set(h2h_df["agent_B"].unique())))
    wins_matrix = wins_matrix.reindex(index=all_agents, columns=all_agents, fill_value=0)
    matches_matrix = wins_matrix + wins_matrix.T
    win_rate_matrix = wins_matrix.div(matches_matrix).fillna(0)

    # Guardar Excel (Cambio solicitado) - Guardamos la matriz con índices
    # Para Excel, reseteamos index para que la primera columna sea visible con nombre
    matrix_to_save = win_rate_matrix.reset_index().rename(columns={'index': 'Agent'})
    save_excel(matrix_to_save, output_dir / "head_to_head_matrix")

    # Plot Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=win_rate_matrix.values,
        x=win_rate_matrix.columns,
        y=win_rate_matrix.index,
        colorscale=[[0.0, "rgb(0,50,0)"], [0.5, "rgb(0,150,0)"], [1.0, "rgb(0,255,0)"]],
        text=np.round(win_rate_matrix.values, 2),
        texttemplate="%{text}",
        colorbar=dict(title="Win Rate")
    ))

    fig.update_layout(
        title="Head-to-Head Win Rate Matrix",
        xaxis_title="Opponent", yaxis_title="Agent",
        height=700, width=700
    )
    
    pio.write_html(fig, file=output_dir / "head_to_head_matrix.html", auto_open=False)
    print("📊 Head-to-Head Matrix generada.")


def run_analysis_pipeline():
    print("--- Iniciando Pipeline de Análisis ---")
    input_dir, output_dir = get_analysis_paths()
    ranking_df, h2h_df = load_data(input_dir)
    
    print("\n--- Generando Visualizaciones (Métrica: Reward / Generations) ---")
    plot_reward_vs_error(ranking_df, output_dir)
    plot_reward_vs_repetitions(ranking_df, output_dir)
    plot_reward_derivative(ranking_df, output_dir)
    
    print("\n--- Generando Reportes Numéricos (XLSX) ---")
    analyze_top_performers(ranking_df, output_dir)
    
    print("\n--- Analizando Enfrentamientos (H2H) ---")
    if not h2h_df.empty:
        analyze_win_rates_and_stats(h2h_df, ranking_df ,output_dir)
        plot_head_to_head_matrix(h2h_df, output_dir)
    else:
        print("⚠️ No hay datos de Head to Head disponibles.")

    print(f"\n[!] Análisis completado. Resultados en: {output_dir.resolve()}")

if __name__ == "__main__":
    try:
        run_analysis_pipeline()
    except KeyboardInterrupt:
        print("\nProceso detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error no controlado: {e}")