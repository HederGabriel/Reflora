import os
import json
from ecossistema import Ecossistema

SAVE_FILE = "reflora_save.json"


class SistemaJogo:
    def __init__(self):
        self.ecossistema = None
        self.historico_jogo = []

    def escolher_bioma(self, i):
        biomas = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
        return biomas[i - 1]

    def confirmar_bioma(self, bioma):
        self.ecossistema = Ecossistema(bioma)

    def adicionar_ao_historico(self):
        e = self.ecossistema
        texto = (
            f"Ano {e.ano}, Mês {e.mes} | "
            f"Plantas {e.plantas} | "
            f"Herbívoros {sum(h.quantidade for h in e.herbivoros.values())} | "
            f"Carnívoros {sum(c.quantidade for c in e.carnivoros.values())}"
        )
        self.historico_jogo.append(texto)

    def salvar(self):
        if not self.ecossistema:
            return
        e = self.ecossistema
        data = {
            "bioma": e.bioma,
            "ano": e.ano,
            "mes": e.mes,
            "plantas": e.plantas,
            "herbivoros": {n: h.quantidade for n, h in e.herbivoros.items()},
            "carnivoros": {n: c.quantidade for n, c in e.carnivoros.items()},
            "historico": self.historico_jogo,
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def carregar(self):
        if not os.path.exists(SAVE_FILE):
            return False

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        self.ecossistema = Ecossistema(data["bioma"])
        e = self.ecossistema

        e.ano = data["ano"]
        e.mes = data["mes"]
        e.plantas = data["plantas"]

        for n, q in data["herbivoros"].items():
            if n in e.herbivoros:
                e.herbivoros[n].quantidade = q

        for n, q in data["carnivoros"].items():
            if n in e.carnivoros:
                e.carnivoros[n].quantidade = q

        self.historico_jogo = data["historico"]
        return True
