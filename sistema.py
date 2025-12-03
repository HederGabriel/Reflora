import os
import json
from ecossistema import Ecossistema

class SistemaJogo:

    def __init__(self):
        self.ecossistema = None
        self.historico_jogo = []
        self.current_save_file = None        # save atualmente carregado
        self.save_limit_reached = False      # usado pelo main
        self.temp_save_file = "saveJogo.json"

    # ---------------------- BIOMA ----------------------
    def escolher_bioma(self, i):
        biomas = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
        return biomas[i - 1]

    def confirmar_bioma(self, bioma):
        self.ecossistema = Ecossistema(bioma)
        self.historico_jogo = []
        self.current_save_file = None        # novo jogo não tem save associado ainda

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
    # ========================= SALVAR ============================
    # ============================================================
    def salvar(self, nome_save=None):
        """
        Fluxo:
        - Se já existe current_save_file → sobrescreve direto.
        - Se NÃO existe save atual:
            - Se usuário forneceu nome → tenta criar.
            - Se já existem 3 saves → cria save temporário e avisa o main.
            - Senão → cria save automático.
        """

        if not self.ecossistema:
            return False

        # dados do jogo
        e = self.ecossistema
        data = {
            "bioma": e.bioma,
            "ano": e.ano,
            "mes": e.mes,
            "plantas": e.plantas,
            "herbivoros": {n: h.quantidade for n, h in e.herbivoros.items()},
            "carnivoros": {n: c.quantidade for n, c in e.carnivoros.items()},
            "historico": self.historico_jogo
        }

        # =====================================================
        # 1) SAVE ATUAL EXISTENTE → sobrescrever
        # =====================================================
        if self.current_save_file:
            destino = self.current_save_file
            with open(destino, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Jogo sobrescrito em {destino}")
            return True

        # =====================================================
        # 2) CRIAR NOVO SAVE
        # =====================================================

        # filtrar apenas saves do jogo
        saves = [
            f for f in os.listdir()
            if f.endswith(".json") and "save" in f.lower()
        ]

        # ----- limite atingido -----
        if len(saves) >= 3:
            with open(self.temp_save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print("⚠ Limite de 3 saves atingido! Criado save temporário.")
            self.save_limit_reached = True
            return False

        # ----- nome manual fornecido -----
        if nome_save:
            destino = f"{nome_save}.json"

            if os.path.exists(destino):
                print("⚠ Esse nome já existe! Escolha outro.")
                return False

        else:
            # nome automático
            idx = 1
            while os.path.exists(f"save{idx}.json"):
                idx += 1
            destino = f"save{idx}.json"

        # criar arquivo
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Novo save criado: {destino}")
        self.current_save_file = destino
        return True

    # ============================================================
    # ========================= CARREGAR ==========================
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
        self.current_save_file = arquivo
        self.save_limit_reached = False

        print(f"Save carregado: {arquivo}")
        return True
