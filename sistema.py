import os
import json
from ecossistema import Ecossistema

class SistemaJogo:

    def __init__(self):
        self.ecossistema = None
        self.historico_jogo = []
        self.current_save_file = None          # save atualmente carregado (string)
        self.save_limit_reached = False        # usado pelo main para abrir tela de substituição
        self.temp_save_file = "saveJogo.json"  # save temporário (não apague)

    # -------------------------------------------------
    # BIOMA
    # -------------------------------------------------
    def escolher_bioma(self, i):
        biomas = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
        return biomas[i - 1]

    def confirmar_bioma(self, bioma):
        self.ecossistema = Ecossistema(bioma)
        self.historico_jogo = []
        self.current_save_file = None   # novo jogo começa sem save associado

    # -------------------------------------------------
    # HISTÓRICO
    # -------------------------------------------------
    def adicionar_ao_historico(self):
        e = self.ecossistema
        texto = (
            f"Ano {e.ano}, Mês {e.mes} | "
            f"Plantas {e.plantas} | "
            f"Herbívoros {sum(h.quantidade for h in e.herbivoros.values())} | "
            f"Carnívoros {sum(c.quantidade for c in e.carnivoros.values())}"
        )
        self.historico_jogo.append(texto)

    def _listar_saves_validos(self):
        """Retorna APENAS saves reais do jogo (ignora jsons que não são saves)."""
        saves = []
        for f in os.listdir():
            if not f.endswith(".json"):
                continue

            if f == self.temp_save_file:
                continue  # ignora o save temporário

            try:
                with open(f, "r", encoding="utf-8") as arq:
                    data = json.load(arq)

                # Só é save válido se contém TODAS as chaves abaixo:
                if all(k in data for k in ("bioma", "ano", "mes", "plantas", "herbivoros", "carnivoros")):
                    saves.append(f)

            except:
                pass  # arquivo inválido → não é save do jogo

        return saves

    # ============================================================
    # ========================= SALVAR ============================
    # ============================================================
    def salvar(self, nome_save=None):
        """
        Fluxo:
        - Se já existe current_save_file  -> sobrescreve
        - Se NÃO existe:
            - Se nome_save foi digitado -> tenta criar
            - Se já houver 3 saves -> cria save temporário "saveJogo.json"
        """

        # Nenhum jogo carregado
        if not self.ecossistema:
            return False

        # Sincroniza histórico antes de salvar
        self.historico_jogo = getattr(self.ecossistema, "historico", [])

        e = self.ecossistema

        # dados do save
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
        # 1) EXISTE SAVE CARREGADO → SOBRESCREVER
        # =====================================================
        if self.current_save_file:
            destino = self.current_save_file
            with open(destino, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"[Salvar] Sobrescrito: {destino}")
            self.save_limit_reached = False
            return True

        # =====================================================
        # 2) CRIANDO NOVO SAVE
        # =====================================================

        # Filtrar apenas saves do jogo (evita contar configs)
        saves = self._listar_saves_validos()

        # -----------------------------------------------------
        # LIMITE DE 3 SAVES -> criar temporário
        # -----------------------------------------------------
        if len(saves) >= 3:

            # cria save temporário (NÃO apaga nada do usuário)
            with open(self.temp_save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print("⚠ Limite de 3 saves atingido. Criado save temporário: saveJogo.json")
            print("⚠ O main deve abrir a tela de substituição.")
            self.save_limit_reached = True
            return False

        # -----------------------------------------------------
        # NOME FOI DIGITADO PELO USUÁRIO
        # -----------------------------------------------------
        if nome_save:
            destino = f"{nome_save}.json"

            # impedir sobrescrever save existente sem intenção
            if os.path.exists(destino):
                print("⚠ Esse nome já existe. Usuário deve digitar outro nome.")
                return False

        else:
            # Criar save automático: save1, save2, save3
            idx = 1
            while os.path.exists(f"save{idx}.json"):
                idx += 1
            destino = f"save{idx}.json"

        # Criar arquivo final
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[Salvar] Novo save criado: {destino}")

        self.current_save_file = destino
        self.save_limit_reached = False
        return True

    # ============================================================
    # ========================= CARREGAR ==========================
    # ============================================================
    def carregar(self, arquivo=None):
        if not arquivo or not os.path.exists(arquivo):
            print("Erro ao carregar: arquivo inexistente.")
            return False

        with open(arquivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        # criar ecossistema a partir do save, passando todo o estado salvo
        self.ecossistema = Ecossistema(bioma=data["bioma"], estado_salvo=data)
        e = self.ecossistema

        # sincroniza histórico do sistema com o do ecossistema
        self.historico_jogo = e.historico.copy()

        # marcar como save carregado
        self.current_save_file = arquivo
        self.save_limit_reached = False

        print(f"[Carregar] Save carregado: {arquivo}")
        return True

    # ============================================================
    # ========================= Histórico ========================
    # ============================================================
    def adicionar_ao_historico(self):
        """Adiciona uma entrada com o estado atual do ecossistema."""
        if not self.ecossistema:
            return

        e = self.ecossistema
        linha = f"Ano {e.ano}, Mês {e.mes} | Plantas {e.plantas} | Herbívoros {sum(h.quantidade for h in e.herbivoros.values())} | Carnívoros {sum(c.quantidade for c in e.carnivoros.values())}"

        if not hasattr(e, "historico"):
            e.historico = []

        e.historico.append(linha)

    def mostrar_historico(self):
        if not self.historico_jogo:
            print("Nenhum histórico ainda.")
        else:
            for linha in self.historico_jogo:
                print(linha)
