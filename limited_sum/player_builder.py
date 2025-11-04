# Importa todas las clases de agentes que quieres gestionar
from limited_sum.player import (
    Always0, Always3, UniformRandom, Focal5, TitForTat,
    Detective, AdaptivePavlov, ContriteTitForTat, GenerousTitForTat, GrimTrigger, 
    CastigadorInfernal, Deterministic_simpletron, PermissiveTitForTat, Player, Game
)

# Diccionario de registro: Mapea el nombre a la CLASE
# Usamos un diccionario para poder instanciar dinámicamente por nombre
AGENT_CLASSES = {
    "Always0": Always0,
    "Always3": Always3,
    "UniformRandom": UniformRandom,
    "Focal5": Focal5,
    "TitForTat": TitForTat,
    "CastigadorInfernal": CastigadorInfernal,
    "Deterministic_simpletron": Deterministic_simpletron,
    "PermissiveTitForTat": PermissiveTitForTat,
    "Detective": Detective,
    "AdaptivePavlov": AdaptivePavlov,
    "ContriteTitForTat": ContriteTitForTat,
    "GenerousTitForTat": GenerousTitForTat,
    "GrimTrigger" : GrimTrigger
    }

# ---------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------

def create_agent(agent_name: str, game: Game, *args, **kwargs) -> Player:
    """
    Instancia un agente mediante su nombre
    Args:
        agent_name: El nombre del agente a instanciar (debe estar en AGENT_CLASSES).
        *args, **kwargs: Argumentos posicionales y de palabra clave 
                         para el constructor de la clase del agente (__init__).

    Returns:
        Una instancia de la clase Player correspondiente.

    Raises:
        ValueError: Si el nombre del agente no está registrado.
    """
    agent_class = AGENT_CLASSES.get(agent_name)
    
    if agent_class is None:
        raise ValueError(f"Agente no registrado: {agent_name}. Opciones: {list(AGENT_CLASSES.keys())}")

    
    return agent_class(game=game, name=agent_name, *args, **kwargs)


def build_several_agents(player_configurations: dict, game: Game,  verbose = False):
    all_agents = {}
    for config in player_configurations:
        agent_name = config["name"]
        agent_type = config["type"]
        args = config.get("args", [])        
        kwargs = config.get("kwargs", {})  

        try:
            # Llama a la función constructora que hace el trabajo pesado
            agent_instance = create_agent(agent_type, game, *args, **kwargs)
            
            # Opcional: Asigna el nombre de la configuración a la instancia
            # Esto depende de si tus clases Player tienen un atributo 'name'
            if hasattr(agent_instance, 'name'):
                agent_instance.name = agent_name
                
            all_agents[agent_name] = agent_instance
            if verbose:
                print(f"✅ Instanciado: {agent_name} ({agent_instance})")
            
        except ValueError as e:
            print(f"❌ Error al instanciar {agent_name}: {e}")
            
        except TypeError as e:
            print(f"❌ Error de argumentos en {agent_name} ({agent_type}): {e}")
    return all_agents