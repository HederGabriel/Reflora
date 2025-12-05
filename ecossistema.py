import random
from biomas import (
    configurar_amazonia,
    configurar_cerrado,
    configurar_pantanal,
    configurar_caatinga
)
from animais import Herbivoro, Carnivoro

class Ecossistema:
    def __init__(self, bioma, estado_salvo=None):  # recebe estado_salvo
        self.bioma = bioma
        self.mes = 1
        self.ano = 1

        # Configuração inicial do bioma
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

        # Inicializa plantas e animais
        self.plantas = config["plantas"]
        self.herbivoros = {
            nome: Herbivoro(nome, info["quantidade"], info["consumo"])
            for nome, info in config["herbivoros"].items()
        }
        self.carnivoros = {
            nome: Carnivoro(nome, info["quantidade"], info["consumo"])
            for nome, info in config["carnivoros"].items()
        }

        # 🔹 Histórico de ações
        self.historico = []

        # Se veio estado salvo, aplica os valores
        if estado_salvo:
            self.ano = estado_salvo.get("ano", self.ano)
            self.mes = estado_salvo.get("mes", self.mes)
            self.plantas = estado_salvo.get("plantas", self.plantas)

            # Atualiza quantidades de herbívoros
            for nome, quantidade in estado_salvo.get("herbivoros", {}).items():
                if nome in self.herbivoros:
                    self.herbivoros[nome].quantidade = quantidade

            # Atualiza quantidades de carnívoros
            for nome, quantidade in estado_salvo.get("carnivoros", {}).items():
                if nome in self.carnivoros:
                    self.carnivoros[nome].quantidade = quantidade

            # Histórico do save
            self.historico = estado_salvo.get("historico", []).copy()

    # --------------------------------------------------
    # Adicionar elementos
    # --------------------------------------------------
    def adicionar_elementos(self, tipo):
        if tipo == "plantas":
            self.plantas += random.randint(150, 250)
        elif tipo == "herbivoros":
            for h in self.herbivoros.values():
                h.quantidade += random.randint(15, 40)
        elif tipo == "carnivoros":
            for c in self.carnivoros.values():
                c.quantidade += random.randint(1, 3)

    # --------------------------------------------------
    # Simular passagem de mês
    # --------------------------------------------------
    def simular_mes(self):
        self.mes += 1
        if self.mes > 12:
            self.mes = 1
            self.ano += 1

        # Crescimento de plantas
        self.plantas += random.randint(50, 100)
        self.plantas = max(0, min(self.plantas, 1000))

        # Herbívoros consomem plantas
        for herbivoro in self.herbivoros.values():
            self.plantas = herbivoro.consumir(self.plantas)

        # Carnívoros consomem herbívoros
        total_herbivoros = sum(h.quantidade for h in self.herbivoros.values())
        for carnivoro in self.carnivoros.values():
            restos = carnivoro.consumir(total_herbivoros)
            for herbivoro in self.herbivoros.values():
                if restos <= 0:
                    break
                perda = min(herbivoro.quantidade, restos)
                herbivoro.quantidade -= perda
                restos -= perda

        # Reprodução e envelhecimento
        for animal in list(self.herbivoros.values()) + list(self.carnivoros.values()):
            animal.reproduzir()
            animal.envelhecer()

    # --------------------------------------------------
    # Registrar histórico de ações
    # --------------------------------------------------
    def registrar_historico(self, acao):
        """Registra o estado do ecossistema após uma ação."""
        linha = (
            f"Ano {self.ano}, Mês {self.mes} | "
            f"Plantas {self.plantas} | "
            f"Herbívoros {sum(h.quantidade for h in self.herbivoros.values())} | "
            f"Carnívoros {sum(c.quantidade for c in self.carnivoros.values())} | "
            f"Ação: {acao}"
        )
        self.historico.append(linha)
