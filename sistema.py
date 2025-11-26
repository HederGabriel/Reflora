import os
import json
from ecossistema import Ecossistema

class SistemaJogo:
    def __init__(self):
        self.ecossistema = None
        self.historico_jogo = []
        self.current_save_file = None  # Arquivo atualmente carregado

    # ---------------------- BIOMA ----------------------
    def escolher_bioma(self, i):
        biomas = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
        return biomas[i - 1]

    def confirmar_bioma(self, bioma):
        self.ecossistema = Ecossistema(bioma)
        self.historico_jogo = []           # limpa histórico para jogo novo
        self.current_save_file = None      # <-- ESSENCIAL: permite criar save novo


    # ---------------------- HISTÓRICO ----------------------
    def adicionar_ao_historico(self):
        e = self.ecossistema
        texto = (
            f"Ano {e.ano}, Mês {e.mes} | "
            f"Plantas {e.plantas} | "
            f"Herbívoros {sum(h.quantidade for h in e.herbivoros.values())} | "
            f"Carnívoros {sum(c.quantidade for c in e.carnivoros.values())}"
        )
        self.historico_jogo.append(texto)

    # ============================================================
    # =====================    SALVAR     =========================
    # ============================================================
    def salvar(self, arquivo=None):
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

        # --- 1) Se usuário informou um arquivo → sobrescrever ---
        if arquivo:
            destino = arquivo

        # --- 2) Se já carregou um save antes → sobrescrever o mesmo ---
        elif self.current_save_file:
            destino = self.current_save_file

        # --- 3) Criar novo save (se houver menos de 3 saves) ---
        else:
            saves = [f for f in os.listdir() if f.startswith("save") and f.endswith(".json")]

            if len(saves) >= 3:
                print("Limite de 3 saves atingido! Apague algum save para criar outro.")
                return

            # Escolhe save1, save2 ou save3
            idx = 1
            while os.path.exists(f"save{idx}.json"):
                idx += 1

            destino = f"save{idx}.json"

        # ----------------- SALVANDO ------------------
        with open(destino, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Jogo salvo em {destino}")
        self.current_save_file = destino

    # ============================================================
    # =====================    CARREGAR    ========================
    # ============================================================
    def carregar(self, arquivo=None):
        if not arquivo or not os.path.exists(arquivo):
            return False

        with open(arquivo, "r") as f:
            data = json.load(f)

        self.ecossistema = Ecossistema(data["bioma"])
        e = self.ecossistema
        e.ano = data["ano"]
        e.mes = data["mes"]
        e.plantas = data["plantas"]

        for nome, qtd in data["herbivoros"].items():
            if nome in e.herbivoros:
                e.herbivoros[nome].quantidade = qtd

        for nome, qtd in data["carnivoros"].items():
            if nome in e.carnivoros:
                e.carnivoros[nome].quantidade = qtd

        self.historico_jogo = data.get("historico", [])
        self.current_save_file = arquivo  # agora este save é o save atual

        print(f"Save {arquivo} carregado")
        return True
