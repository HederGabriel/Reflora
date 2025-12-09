from biomas import (
    configurar_amazonia,
    configurar_cerrado,
    configurar_pantanal,
    configurar_caatinga
)
from animais import Herbivoro, Carnivoro

class Ecossistema:
    def __init__(self, bioma, estado_salvo=None):
        self.bioma = bioma
        self.mes = 12
        self.ano = 4

        # Configuração inicial por bioma + capacidade de plantas
        if bioma == "Amazônia":
            config = configurar_amazonia()
            self.capacidade_plantas = 3500
        elif bioma == "Cerrado":
            config = configurar_cerrado()
            self.capacidade_plantas = 2500
        elif bioma == "Pantanal":
            config = configurar_pantanal()
            self.capacidade_plantas = 3000
        elif bioma == "Caatinga":
            config = configurar_caatinga()
            self.capacidade_plantas = 1800
        else:
            raise ValueError("Bioma inválido.")

        # Plantas
        self.plantas = int(config.get("plantas", 0))

        # Animais
        self.herbivoros = {
            n: Herbivoro(n, d["quantidade"], d["consumo"])
            for n, d in config.get("herbivoros", {}).items()
        }
        self.carnivoros = {
            n: Carnivoro(n, d["quantidade"], d["consumo"])
            for n, d in config.get("carnivoros", {}).items()
        }

        # Histórico
        self.historico = []

        # Roda estado salvo se houver
        if estado_salvo:
            self.ano = estado_salvo.get("ano", self.ano)
            self.mes = estado_salvo.get("mes", self.mes)
            self.plantas = estado_salvo.get("plantas", self.plantas)

            for nome, quantidade in estado_salvo.get("herbivoros", {}).items():
                if nome in self.herbivoros:
                    self.herbivoros[nome].quantidade = int(quantidade)

            for nome, quantidade in estado_salvo.get("carnivoros", {}).items():
                if nome in self.carnivoros:
                    self.carnivoros[nome].quantidade = int(quantidade)

            self.historico = estado_salvo.get("historico", []).copy()

    # dentro da classe Ecossistema
    def verificar_fim_jogo(self):
        """
        Retorna:
            None -> jogo continua
            "vitória" -> ecossistema equilibrado
            "derrota" -> ecossistema colapsou
        """
        total_herb = sum(h.quantidade for h in self.herbivoros.values())
        total_carn = sum(c.quantidade for c in self.carnivoros.values())

        # Condições de derrota
        if self.plantas <= 0 or total_herb <= 0 or total_carn <= 0:
            return "derrota"

        # Condições de vitória (meta: manter ecossistema saudável por 5 anos)
        if self.ano >= 5 and self.plantas > 0 and total_herb > 0 and total_carn > 0:
            return "vitória"

        return None

    # -------------------------------------------
    # Simular passagem de mês
    # -------------------------------------------
    def simular_mes(self):
        # Avança tempo
        self.mes += 1
        if self.mes > 12:
            self.mes = 1
            self.ano += 1

        # 1) Herbívoros comem
        for h in self.herbivoros.values():
            self.plantas = h.consumir(self.plantas)

        # 2) Herbívoros reproduzem
        for h in self.herbivoros.values():
            h.reproduzir()

        # 3) Herbívoros envelhecem
        for h in self.herbivoros.values():
            h.envelhecer()

        # 4) Atualiza total de herbívoros antes de carnívoros
        total_herb = sum(h.quantidade for h in self.herbivoros.values())

        # 5) Carnívoros caçam herbívoros
        for c in self.carnivoros.values():
            if c.quantidade <= 0:
                continue

            necessidade = int(c.quantidade * (c.consumo * 0.5))
            eficiencia_predador = 0.85
            presas_disponiveis = total_herb
            presas_capturadas = min(necessidade, presas_disponiveis)
            presas_efetivas = int(presas_capturadas * eficiencia_predador)

            if presas_efetivas > 0:
                restantes = presas_efetivas
                especies = list(self.herbivoros.values())
                total_atual = total_herb

                for h in especies:
                    if restantes <= 0 or total_atual <= 0:
                        break
                    proporcao = h.quantidade / total_atual if total_atual > 0 else 0
                    perdas = int(round(presas_efetivas * proporcao))
                    perdas = min(perdas, h.quantidade, restantes)
                    h.quantidade -= perdas
                    restantes -= perdas
                    total_atual -= perdas

                # Distribuir restantes se houver
                if restantes > 0:
                    for h in especies:
                        if restantes <= 0:
                            break
                        retirar = min(h.quantidade, restantes)
                        h.quantidade -= retirar
                        restantes -= retirar

                total_herb = sum(h.quantidade for h in self.herbivoros.values())

            # Fome gradual dos carnivoros
            if presas_efetivas < necessidade:
                c.fome = getattr(c, "fome", 0) + 1
            else:
                c.fome = 0

            if c.fome >= 3:
                c.quantidade = max(0, c.quantidade - 1)
                c.fome = 0

        # 6) Carnívoros reproduzem
        for c in self.carnivoros.values():
            c.reproduzir()

        # 7) Carnívoros envelhecem
        for c in self.carnivoros.values():
            c.envelhecer()
