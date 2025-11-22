import os
import pandas as pd
from pathlib import Path
import numpy as np

from limited_sum import Game, build_several_agents, Evolution

# -----------------------------------------------------------------------------
# LÓGICA PRINCIPAL
# -----------------------------------------------------------------------------

def get_user_input():
    """
    Encapsulamos la lógica de interacción con el usuario para mantener el scope limpio.
    Se realizan conversiones de tipo básicas.
    """
    print("--- Configuración del Match ---")
    folder_name = "results/" +  input("Nombre de la carpeta para guardar ficheros: ").strip()
    
    # Usamos float para probabilidades y validamos rangos más adelante
    min_error = float(input("Probabilidad mínima de error (0.0 - 1.0): "))
    max_error = float(input("Probabilidad máxima de error (0.0 - 1.0): "))
    
    min_rep = int(input("Mínimo número de repeticiones: "))
    max_rep = int(input("Máximo número de repeticiones: "))
    
    duration_input = float(input("Duración del Match ( < 1 = probabilidad, >= 1 = n_generaciones): "))
    
    return folder_name, min_error, max_error, min_rep, max_rep, duration_input

def generate_ranges(min_val, max_val, step, is_integer=False):
    """
    Generador auxiliar para crear rangos inclusivos.
    Maneja tanto floats como enteros.
    """
    current = min_val
    while current <= max_val:
        yield int(current) if is_integer else round(current, 4)
        current += step

def run_match_simulation(all_agents):
    # 1. Obtención de inputs
    folder_name, min_error, max_error, min_rep, max_rep, n_rounds = get_user_input()

    # 2. Configuración de directorios (Uso de pathlib por ser más robusto que os.path)
    base_path = Path(folder_name)
    try:
        base_path.mkdir(parents=True, exist_ok=True)
        print(f"Directorio '{base_path.resolve()}' preparado.")
    except Exception as e:
        print(f"Error crítico creando el directorio: {e}")
        return

    # Definición de rutas de salida
    ranking_path = base_path / "ranking_data.csv"
    head_to_head_path = base_path / "head_to_head_data.csv"

    # 3. Lógica de control de duración (Strategy Pattern simplificado)
    # Determinamos si pasamos generations o termination_prob al constructor

    rows = []
    head_to_head_data = pd.DataFrame()

    STEP_ERROR = 0.05
    STEP_REP = 2
    N_GENERATIONS = 15 # A partir de 15 generaciones, la evolucion converge

    # 4. Bucles de simulación
    # Usamos generadores para evitar problemas de punto flotante en el range()
    error_range = generate_ranges(min_error, max_error, STEP_ERROR)
    
    for error_p in error_range:
        # Reiniciamos el generador de repeticiones para cada error
        rep_range = generate_ranges(min_rep, max_rep, STEP_REP, is_integer=True)
        
        for repetitions in rep_range:
            print(f"--- Ejecutando: Error {error_p} | Repeticiones {repetitions} ---")
            
            # Instanciación dinámica
            evolution = Evolution(
                players = all_agents.values(), 
                generations=N_GENERATIONS,
                error=error_p,
                repetitions=repetitions,
                n_rounds=n_rounds,                
            )
            
            evolution.play(do_print=True)
            # 5. Extracción de datos (Optimización)
            for agent_obj, reward in evolution.cumulative_ranking.items():
                rows.append({
                    "error_prob": error_p,
                    "n_repetitions": repetitions,
                    "agent_name": agent_obj.name,
                    "reward": reward,
                    "n_generations": N_GENERATIONS
                })

            # Concatenación de DataFrames
            current_h2h = evolution.get_head_to_head_rewards()
            if not current_h2h.empty:
                head_to_head_data = pd.concat([head_to_head_data, current_h2h], ignore_index=True)

    # 6. Persistencia de datos
    if rows:
        ranking_df = pd.DataFrame(rows)
        ranking_df.to_csv(ranking_path, index=False)
        print(f"Guardado: {ranking_path}")
    else:
        print("Advertencia: No se generaron datos de ranking.")

    if not head_to_head_data.empty:
        head_to_head_data.to_csv(head_to_head_path, index=False)
        print(f"Guardado: {head_to_head_path}")

def get_all_agents(game):
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
            "name": "AdaptivePavlov_random_always_coop",
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
    return all_agents
if __name__ == "__main__":
    game = Game()
    all_agents = get_all_agents(game)
    try:
        run_match_simulation(all_agents)
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")