import random
from biomas import (
    configurar_amazonia,
    configurar_cerrado,
    configurar_pantanal,
    configurar_caatinga
)
from animais import Herbivoro, Carnivoro


class Ecossistema:
    def __init__(self, bioma):
        self.bioma = bioma
        self.mes = 1
        self.ano = 1

        if bioma == "Amazônia":
            config = configurar_amazonia()
        elif bioma == "Cerrado":
            config = configurar_cerrado()
        elif bioma == "Pantanal":
            config = configurar_pantanal()
        elif bioma == "Caatinga":
            config = configurar_caatinga()
        else:
            raise ValueError("Bioma inválido.")

        self.plantas = config["plantas"]
        self.herbivoros = {
            nome: Herbivoro(nome, info["quantidade"], info["consumo"])
            for nome, info in config["herbivoros"].items()
        }
        self.carnivoros = {
            nome: Carnivoro(nome, info["quantidade"], info["consumo"])
            for nome, info in config["carnivoros"].items()
        }

    def adicionar_elementos(self, tipo):
        if tipo == "plantas":
            self.plantas += random.randint(150, 250)
        elif tipo == "herbivoros":
            for h in self.herbivoros.values():
                h.quantidade += random.randint(15, 40)
        elif tipo == "carnivoros":
            for c in self.carnivoros.values():
                c.quantidade += random.randint(1, 3)

    def simular_mes(self):
        self.mes += 1
        if self.mes > 12:
            self.mes = 1
            self.ano += 1

        self.plantas += random.randint(50, 100)
        self.plantas = max(0, min(self.plantas, 1000))

        for herbivoro in self.herbivoros.values():
            self.plantas = herbivoro.consumir(self.plantas)

        for carnivoro in self.carnivoros.values():
            total = sum(h.quantidade for h in self.herbivoros.values())
            restos = carnivoro.consumir(total)
            for herbivoro in self.herbivoros.values():
                if restos <= 0:
                    break
                loss = min(herbivoro.quantidade, restos)
                herbivoro.quantidade -= loss
                restos -= loss

        for animal in list(self.herbivoros.values()) + list(self.carnivoros.values()):
            animal.reproduzir()
            animal.envelhecer()
