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
        self.current_save_file = None      # permite criar save novo

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
    # =====================    SALVAR     ========================
    # ============================================================
    def salvar(self, nome_save=None, criando_novo_jogo=False):
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

        # Se está carregando um save e NÃO é um jogo novo → sobrescrever
        if self.current_save_file and not criando_novo_jogo:
            destino = self.current_save_file

        # Se usuário digitou nome de save → usar esse nome
        elif nome_save:
            destino = f"{nome_save}.json"
            if os.path.exists(destino) and destino != self.current_save_file:
                print(f"Save '{destino}' já existe! Escolha outro nome.")
                return

        # Criar novo save automático (save1, save2, save3)
        else:
            idx = 1
            while os.path.exists(f"save{idx}.json") and idx <= 3:
                idx += 1
            if idx > 3:
                print("Limite de 3 saves atingido! Apague algum save para criar outro.")
                return
            destino = f"save{idx}.json"

        # Salva no arquivo definido
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Jogo salvo em {destino}")
        self.current_save_file = destino

    # ============================================================
    # =====================    CARREGAR    =======================
    # ============================================================
    def carregar(self, arquivo=None):
        if not arquivo or not os.path.exists(arquivo):
            return False

        with open(arquivo, "r", encoding="utf-8") as f:
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
        self.current_save_file = arquivo  # este save é o atual

        print(f"Save {arquivo} carregado")
        return True
