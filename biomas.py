import random


def configurar_amazonia():
    return {
        "plantas": 500,
        "herbivoros": {
            "Preguiça": {"quantidade": 20, "consumo": random.randint(1, 2)},
            "Anta": {"quantidade": 15, "consumo": random.randint(1, 2)},
            "Capivara": {"quantidade": 20, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Onça-pintada": {"quantidade": 5, "consumo": random.randint(1, 2)},
            "Jacaré-açu": {"quantidade": 5, "consumo": random.randint(1, 2)},
            "Harpia": {"quantidade": 4, "consumo": random.randint(1, 2)}
        }
    }


def configurar_cerrado():
    return {
        "plantas": 450,
        "herbivoros": {
            "Tamanduá-bandeira": {"quantidade": 15, "consumo": random.randint(1, 2)},
            "Tatu-canastra": {"quantidade": 10, "consumo": random.randint(1, 2)},
            "Veado-campeiro": {"quantidade": 12, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Lobo-guará": {"quantidade": 6, "consumo": random.randint(1, 2)},
            "Jaguatirica": {"quantidade": 5, "consumo": random.randint(1, 2)},
            "Gavião-carrapateiro": {"quantidade": 4, "consumo": random.randint(1, 2)}
        }
    }


def configurar_pantanal():
    return {
        "plantas": 480,
        "herbivoros": {
            "Capivara": {"quantidade": 18, "consumo": random.randint(1, 2)},
            "Cervo-do-pantanal": {"quantidade": 12, "consumo": random.randint(1, 2)},
            "Tatu-peba": {"quantidade": 10, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Onça-pintada": {"quantidade": 6, "consumo": random.randint(1, 2)},
            "Ariranha": {"quantidade": 5, "consumo": random.randint(1, 2)},
            "Tuiuiú": {"quantidade": 4, "consumo": random.randint(1, 2)}
        }
    }


def configurar_caatinga():
    return {
        "plantas": 400,
        "herbivoros": {
            "Preá": {"quantidade": 15, "consumo": random.randint(1, 2)},
            "Mocó": {"quantidade": 12, "consumo": random.randint(1, 2)},
            "Iguana": {"quantidade": 10, "consumo": random.randint(1, 2)}
        },
        "carnivoros": {
            "Asa-branca": {"quantidade": 6, "consumo": random.randint(1, 2)},
            "Gato-maracajá": {"quantidade": 5, "consumo": random.randint(1, 2)},
            "Raposa": {"quantidade": 7, "consumo": random.randint(1, 2)}
        }
    }
