import random

# ---------------------------------------------------------
# AMAZÔNIA — bioma mais estável e produtivo
# ---------------------------------------------------------
def configurar_amazonia():
    return {
        "plantas": 600,  # antes 500
        "herbivoros": {
            "Preguiça": {"quantidade": 16, "consumo": random.randint(1, 2)},
            "Anta": {"quantidade": 12, "consumo": random.randint(1, 2)},
            "Capivara": {"quantidade": 18, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Onça-pintada": {"quantidade": 3, "consumo": random.randint(1, 2)},
            "Jacaré-açu": {"quantidade": 4, "consumo": random.randint(1, 2)},
            "Harpia": {"quantidade": 4, "consumo": random.randint(1, 2)}
        }
    }


# ---------------------------------------------------------
# CERRADO — menos plantas, animais mais distribuídos
# ---------------------------------------------------------
def configurar_cerrado():
    return {
        "plantas": 520,  # antes 450
        "herbivoros": {
            "Tamanduá-bandeira": {"quantidade": 12, "consumo": random.randint(1, 2)},
            "Tatu-canastra": {"quantidade": 10, "consumo": random.randint(1, 2)},
            "Veado-campeiro": {"quantidade": 14, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Lobo-guará": {"quantidade": 3, "consumo": random.randint(1, 2)},
            "Jaguatirica": {"quantidade": 4, "consumo": random.randint(1, 2)},
            "Gavião-carrapateiro": {"quantidade": 5, "consumo": random.randint(1, 2)}
        }
    }


# ---------------------------------------------------------
# PANTANAL — muita vegetação e herbívoros aquáticos
# ---------------------------------------------------------
def configurar_pantanal():
    return {
        "plantas": 650,  # antes 480
        "herbivoros": {
            "Capivara": {"quantidade": 20, "consumo": random.randint(1, 2)},
            "Cervo-do-pantanal": {"quantidade": 12, "consumo": random.randint(1, 2)},
            "Tatu-peba": {"quantidade": 10, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Onça-pintada": {"quantidade": 3, "consumo": random.randint(1, 2)},
            "Ariranha": {"quantidade": 4, "consumo": random.randint(1, 2)},
            "Tuiuiú": {"quantidade": 5, "consumo": random.randint(1, 2)}
        }
    }


# ---------------------------------------------------------
# CAATINGA — plantas bem menores, herbívoros pequenos
# ---------------------------------------------------------
def configurar_caatinga():
    return {
        "plantas": 450,  # antes 400
        "herbivoros": {
            "Preá": {"quantidade": 14, "consumo": random.randint(1, 2)},
            "Mocó": {"quantidade": 12, "consumo": random.randint(1, 2)},
            "Iguana": {"quantidade": 10, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Asa-branca": {"quantidade": 5, "consumo": random.randint(1, 2)},
            "Gato-maracajá": {"quantidade": 3, "consumo": random.randint(1, 2)},
            "Raposa": {"quantidade": 4, "consumo": random.randint(1, 2)}
        }
    }
