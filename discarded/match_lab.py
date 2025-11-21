# En este script podemos probar configuraciones de Match
# y ver qué estrategias funcionan mejor
OUT_DIR = "./results/"
RANKING_PATH = OUT_DIR + "tournament_results.csv"
HEAD_TO_HEAD_PATH = OUT_DIR + "head_to_head_results.csv"
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel, wilcoxon
import matplotlib.pyplot as plt
from limited_sum import Game, build_several_agents, Evolution
import plotly.graph_objects as go
import plotly.io as pio


game = Game()

# Los agentes que queremos poner a prueba
PLAYER_CONFIGURATIONS = [
    {
        "name": "Always0",
        "type": "Always0",
    },
    {
        "name": "Always3",
        "type": "Always3",
    },
    {
        "name": "UniformRandom",
        "type": "UniformRandom",
    },
    {
        "name": "Focal5",
        "type": "Focal5",
    },
    {
        "name": "TitForTat",
        "type": "TitForTat",
    },
    {
        "name": "CastigadorInfernal",
        "type": "CastigadorInfernal",
    },
    # Optimista: Comieza eligiendo 2, not TFT: Si decide castigar elegira siempre 3
    {
        "name": "Deterministic_simpletron_optimist_notTfT",
        "type": "Deterministic_simpletron",
    },
    # Pesimista: Comieza eligiendo 3
    {
        "name": "Deterministic_simpletron_pesimist_notTfT",
        "type": "Deterministic_simpletron",
        "kwargs": {"pesimist_start": True},
    },
    # TFT punishment: Al castigar, juega como TFT
    {
        "name": "Deterministic_simpletron_optimist_TfT",
        "type": "Deterministic_simpletron",
        "kwargs": {"tit_for_tat_punishment": True},
    },
    {
        "name": "Deterministic_simpletron_pesimist_notTfT",
        "type": "Deterministic_simpletron",
        "kwargs": {"pesimist_start": True, "tit_for_tat_punishment": True},
    },
    {
        "name": "Permisive_TFT_patience_3",
        "type": "PermissiveTitForTat",
    },
    {
        "name": "Permisive_TFT_patience_5",
        "type": "PermissiveTitForTat",
        "kwargs": {
            "initial_patience": 5,
        },
    },
    {
        "name": "Permisive_TFT_patience_10",
        "type": "PermissiveTitForTat",
        "kwargs": {
            "initial_patience": 10,
        },
    },
    {
        "name": "GrimTrigger",
        "type": "GrimTrigger",
    },
    # TFT pero perdona con cierta probabilidad
    {
        "name": "GenerousTitForTat_generous_p_0.1",
        "type": "GenerousTitForTat",
        "kwargs": {"prob_generosidad": 0.1},
    },
    {
        "name": "GenerousTitForTat_generous_p_0.25",
        "type": "GenerousTitForTat",
        "kwargs": {"prob_generosidad": 0.25},
    },
    {
        "name": "GenerousTitForTat_generous_p_0.5",
        "type": "GenerousTitForTat",
        "kwargs": {"prob_generosidad": 0.5},
    },
    {
        "name": "GenerousTitForTat_generous_p_0.75",
        "type": "GenerousTitForTat",
        "kwargs": {"prob_generosidad": 0.75},
    },
    {
        "name": "ContriteTitForTat",
        "type": "ContriteTitForTat",
    },
    # La version determinista cambia de cooperar a rivalizar si no obtiene un beneficio
    {
        "name": "AdaptivePavlov_deterministic",
        "type": "AdaptivePavlov",
    },
    # La version random tiene un 50% de posibilidades de cambiar de estrategia o no
    {
        "name": "AdaptivePavlov_random",
        "type": "AdaptivePavlov",
        "kwargs": {"shift_strategy": "random"},
    },
    # La siguiente version siempre coopera
    {
        "name": "AdaptivePavlov_random",
        "type": "AdaptivePavlov",
        "kwargs": {"shift_strategy": "always_coop"},
    },
    {
        "name": "Detective",
        "type": "Detective",
    },
]

# Instanciamos los agentes:
all_agents = build_several_agents(PLAYER_CONFIGURATIONS, game, verbose=False)
# 'all_agents' ahora contiene un diccionario de todas tus instancias configuradas.
print("\nAgentes listos para el Torneo:")
print(list(all_agents.keys()))


# Torneos -> Vemos  como evoluciona un agente a medida que cambia la probabilidad de equivocarse y el numero de veces que juega frente al mismo contrincante
DO_PLAY = (
    True  # Para controlar si queremos calcular y sobreescribir los resultados o no
)
if DO_PLAY:
    #  Columnas: error_prob, n_repetitions, agent_name, reward
    rows = []
    head_to_head_data = pd.DataFrame()
    for _error in range(0, 26, 5):
        error_p = _error / 100
        for repetitions in range(1, 9, 2):
            print(
                f"Testing iteration:\nError probability: {error_p}\nNumber of repetitions (agent vs agent): {repetitions}"
            )
            evolution = Evolution(
                all_agents.values(),
                generations=10,
                error=error_p,
                repetitions=repetitions,
                n_rounds=0.1 #10% de posibilidades de acabar cada match
            )
            evolution.play(do_print=True)
            # Obtenemos el ranking de la evolucion
            for player_name, player_object in all_agents.items():
                for ranking_player_object, ranking_reward in evolution.ranking.items():
                    reward = None
                    if ranking_player_object.name == player_name:
                        reward = ranking_reward
                        new_row = {
                            "error_prob": error_p,
                            "n_repetitions": repetitions,
                            "agent_name": player_name,
                            "reward": reward,
                        }
                        rows.append(new_row)
            # Obtenemos la informacion de los enfrentamientos por parejas
            head_to_head_data = pd.concat(
                [head_to_head_data, evolution.get_head_to_head_rewards()]
            )

    ranking_data = pd.DataFrame(rows)
    ranking_data.to_csv(RANKING_PATH, index=False)
    head_to_head_data.to_csv(HEAD_TO_HEAD_PATH, index=False)
else:
    ranking_data = pd.read_csv(RANKING_PATH)
    head_to_head_data = pd.read_csv(HEAD_TO_HEAD_PATH)
print("Ranking data:")
print(ranking_data.sort_values(by="reward", ascending=False))
# === 1. Reward vs error_prob ===
fig = go.Figure()

# Agrupar por agente y número de repeticiones, calculando la reward media
ranking_mean = (
    ranking_data[["agent_name", "error_prob", "reward"]] #[ranking_data["n_repetitions"] == max(ranking_data["n_repetitions"])]
    .groupby(["agent_name", "error_prob"])["reward"]
    .mean()
    .reset_index()
)


# Crear la figura
fig = go.Figure()

# Dibujar cada agente
for agent_name, group in ranking_mean.groupby("agent_name"):
    group_sorted = group.sort_values("error_prob")

    fig.add_trace(
        go.Scatter(
            x=group_sorted["error_prob"],
            y=group_sorted["reward"],
            mode="lines+markers",
            name=f"{agent_name}",
        )
    )

# Estética
fig.update_layout(
    title="Reward media por agente vs error_prob",
    xaxis_title="Error probability",
    yaxis_title="Mean Reward",
    hovermode="x unified",
)


# guardo como HTML interactivo
pio.write_html(fig, file=f"{OUT_DIR}/reward_vs_error_prob.html", auto_open=False)

# === 2. Reward vs n_repetitions ===
fig2 = go.Figure()
ranking_mean = (
    ranking_data[["agent_name", "n_repetitions", "reward"]] 
    .groupby(["agent_name", "n_repetitions"])["reward"]
    .mean()
    .reset_index()
)

for agent_name, group in ranking_mean.groupby("agent_name"):
    group_sorted = group.sort_values("n_repetitions")
    fig2.add_trace(
        go.Scatter(
            x=group_sorted["n_repetitions"],
            y=group_sorted["reward"],
            mode="lines+markers",
            name=agent_name,
        )
    )

fig2.update_layout(
    title="Reward por agente vs n_repetitions",
    xaxis_title="Número de repeticiones",
    yaxis_title="Reward",
    hovermode="x unified",
)

pio.write_html(fig2, file=f"{OUT_DIR}/reward_vs_repetitions.html", auto_open=False)

print("✅ Plots interactivos generados correctamente")


fig3 = go.Figure()

# Partimos del ranking_mean del gráfico anterior
ranking_mean = (
    ranking_data[["agent_name", "n_repetitions", "reward"]] 
    .groupby(["agent_name", "n_repetitions"])["reward"]
    .mean()
    .reset_index()
)

derivative_list = []

for agent_name, group in ranking_mean.groupby("agent_name"):
    group_sorted = group.sort_values("n_repetitions")

    # Diferencia discreta: Δreward / Δn
    # Como Δn casi siempre es 1, es básicamente la pendiente entre puntos sucesivos
    d_reward = np.diff(group_sorted["reward"])
    d_n = np.diff(group_sorted["n_repetitions"])

    derivative = d_reward / d_n  # vector de pendientes
    n_midpoints = group_sorted["n_repetitions"][:-1] + d_n / 2

    # Guardamos en caso de necesitar análisis adicional
    tmp = pd.DataFrame({
        "agent_name": agent_name,
        "n_repetitions_mid": n_midpoints,
        "d_reward_dn": derivative
    })
    derivative_list.append(tmp)

    # Añadir al gráfico
    fig3.add_trace(
        go.Scatter(
            x=n_midpoints,
            y=derivative,
            mode="lines+markers",
            name=agent_name,
        )
    )

# Concatenamos las derivadas completas (opcional por si lo necesitas luego)
ranking_derivative = pd.concat(derivative_list, ignore_index=True)

# Estética
fig3.update_layout(
    title="Velocidad de Mejora del Reward vs n_repetitions",
    xaxis_title="n_repetitions (punto medio)",
    yaxis_title="d(Reward)/d(n_repetitions)",
    hovermode="x unified",
)

# Guardar en disco
output_file = f"{OUT_DIR}/reward_derivative_vs_repetitions.html"
pio.write_html(fig3, file=output_file, auto_open=False)

print(f"✅ Derivada generada y guardada en: {output_file}")


# ========================
# Top 3 modelos por tipo de torneo
# ========================

# agrupar por tipo de torneo y agente, calculando estadísticas
grouped = (
    ranking_data.groupby(["error_prob", "n_repetitions", "agent_name"])["reward"]
    .agg(["mean", "std", "min", "max"])
    .reset_index()
)


# función auxiliar para obtener top 3 por mean reward
def top3(df):
    # orden descendente por mean
    df = df.sort_values("mean", ascending=False)
    return df.head(3)


# aplicar top3 sin generar FutureWarning
best_models = grouped.groupby(["error_prob", "n_repetitions"], group_keys=False).apply(
    top3
)

# guardo resultados
best_models.to_csv(OUT_DIR + "best_models_for_tournament_type.csv", index=False)

# imprimir en el formato solicitado
for (err, reps), subdf in best_models.groupby(["error_prob", "n_repetitions"]):
    print("\nTournament:")
    print(f"Error probability: {err} | Number of repetitions: {reps}")
    for _, row in subdf.iterrows():
        print(
            f"    - {row['agent_name']}: mean={row['mean']:.4f}, std={row['std']:.4f}, min={row['min']:.4f}, max={row['max']:.4f}"
        )


# ========================
# Win rate por agente
# ========================

# Contar victorias por agente (winner es el nombre del agente ganador)
win_counts = head_to_head_data["winner"].value_counts()

# Como cada fila es un match entre dos agentes, cada agente participa en dos columnas
# extraigo todos los agentes
all_agents = pd.concat([head_to_head_data["agent_A"], head_to_head_data["agent_B"]])
match_counts = all_agents.value_counts()

# Win rate = victorias totales / partidas jugadas totales
win_rate = (win_counts / match_counts).fillna(0)

print("Win rate por agente:")
print(win_rate.sort_values(ascending=False))

# ========================
# Reward media, std y median
# ========================

# Agrupar por agent_A y reward_A / agent_B y reward_B requiere apilar los datos
# genero primero un dataframe "long" con agent y reward
dfA = head_to_head_data[["agent_A", "reward_A"]].rename(
    columns={"agent_A": "agent", "reward_A": "reward"}
)
dfB = head_to_head_data[["agent_B", "reward_B"]].rename(
    columns={"agent_B": "agent", "reward_B": "reward"}
)
rewards_long = pd.concat([dfA, dfB], ignore_index=True)

reward_stats = (
    rewards_long.groupby("agent")["reward"].agg(["mean", "std", "median"]).fillna(0)
)
print("\nEstadísticas de recompensas:")
print(reward_stats.sort_values(by="median", ascending=False))
reward_stats.sort_values(by="median", ascending=False).reset_index().to_csv(
    OUT_DIR + "reward_stats.csv", index=False
)
# ========================
# Matriz de win rate A vs B
# ========================


# Crear una tabla de frecuencia de victorias: filas = agente ganador, columnas = perdedor
# Para esto, primero identifico al perdedor
def get_loser(row):
    if row["winner"] == row["agent_A"]:
        return row["agent_B"]
    elif row["winner"] == row["agent_B"]:
        return row["agent_A"]
    else:
        return None


head_to_head_data["loser"] = head_to_head_data.apply(get_loser, axis=1)

# Tabla de conteo de victorias por ganador vs perdedor
win_matrix_counts = pd.crosstab(head_to_head_data["winner"], head_to_head_data["loser"])

# Ahora normalizamos por fila para obtener el win rate contra cada oponente
win_matrix = win_matrix_counts.div(win_matrix_counts.sum(axis=1), axis=0).fillna(0)

# Guardar matriz en CSV
win_matrix.to_csv(OUT_DIR + "head_to_head_matrix.csv", index=False)

# ========================
# Guardar matriz como heatmap (sin visualizar)
# ========================
fig = go.Figure(
    data=go.Heatmap(
        z=win_matrix.values,
        x=win_matrix.columns,
        y=win_matrix.index,
        colorscale=[
            [0.0, "rgb(0,50,0)"],  # verde muy oscuro
            [0.5, "rgb(0,150,0)"],  # verde medio
            [1.0, "rgb(0,255,0)"],  # verde puro
        ],
        colorbar=dict(title="Win rate"),
    )
)

# seteo labels y títulos
fig.update_layout(
    title="Head-to-head win rate matrix",
    xaxis_title="Opponent",
    yaxis_title="Agent",
)

# guardo en HTML interactivo
pio.write_html(fig, file=f"{OUT_DIR}/head_to_head_matrix.html", auto_open=False)

print("✅ Plot interactivo guardado correctamente")

print("\nMatriz head-to-head guardada en head_to_head_matrix.csv y head_to_head.png")
