import random
from biomas import configurar_amazonia, configurar_cerrado, configurar_pantanal, configurar_caatinga
from animais import Herbivoro, Carnivoro


class Ecossistema:
    def __init__(self, bioma):
        self.bioma = bioma
        self.mes = 1
        self.ano = 1

        if self.bioma == "Amazônia":
            config = configurar_amazonia()
        elif self.bioma == "Cerrado":
            config = configurar_cerrado()
        elif self.bioma == "Pantanal":
            config = configurar_pantanal()
        elif self.bioma == "Caatinga":
            config = configurar_caatinga()
        else:
            raise ValueError("Bioma inválido!")

        self.plantas = config["plantas"]
        self.herbivoros = {nome: Herbivoro(nome, info["quantidade"], info["consumo"]) for nome, info in
                           config["herbivoros"].items()}
        self.carnivoros = {nome: Carnivoro(nome, info["quantidade"], info["consumo"]) for nome, info in
                           config["carnivoros"].items()}

    def exibir_status(self):
        print(f"Relatório do Bioma: {self.bioma}")
        print(f"Ano: {self.ano}, Mês: {self.mes}")
        print("Herbívoros:")
        for nome, animal in self.herbivoros.items():
            print(f"  {nome}: {animal.quantidade}")
        print("Carnívoros:")
        for nome, animal in self.carnivoros.items():
            print(f"  {nome}: {animal.quantidade}")
        print(f"Plantas: {self.plantas}")

    def adicionar_elementos(self, tipo):
        if tipo == "plantas":
            self.plantas += random.randint(150, 250)
        elif tipo == "herbivoros":
            for nome, herbivoro in self.herbivoros.items():
                herbivoro.quantidade += random.randint(15, 40)  # Adiciona herbívoros corretamente
        elif tipo == "carnivoros":
            for nome, carnivoro in self.carnivoros.items():
                carnivoro.quantidade += random.randint(1, 3)

    def simular_mes(self):
        self.mes += 1
        if self.mes > 12:
            self.mes = 1
            self.ano += 1

        # Atualiza plantas
        self.plantas += random.randint(50, 100)
        self.plantas = max(0, min(self.plantas, 1000))

        # Herbívoros consomem plantas
        for herbivoro in self.herbivoros.values():
            self.plantas = herbivoro.consumir(self.plantas)
            herbivoro.quantidade = max(0, min(herbivoro.quantidade, 50))

        # Carnívoros consomem herbívoros
        for carnivoro in self.carnivoros.values():
            total_herbivoros = sum(h.quantidade for h in self.herbivoros.values())
            herbivoros_consumidos = carnivoro.consumir(total_herbivoros)

            if herbivoros_consumidos > 0:
                for herbivoro in self.herbivoros.values():
                    if herbivoros_consumidos <= 0:
                        break
                    consumo_por_herbivoro = min(herbivoro.quantidade, herbivoros_consumidos)
                    herbivoro.quantidade -= consumo_por_herbivoro
                    herbivoros_consumidos -= consumo_por_herbivoro

        # Reprodução e envelhecimento (só no final do mês)
        for animal in list(self.herbivoros.values()) + list(self.carnivoros.values()):
            animal.reproduzir()
            animal.envelhecer()
            if isinstance(animal, Carnivoro):
                animal.quantidade = max(0, min(animal.quantidade, 20))