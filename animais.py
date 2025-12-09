import random
import math

class Animal:
    def __init__(self, nome, quantidade, consumo):
        self.quantidade = int(max(0, quantidade))
        self.consumo = float(consumo)

    def consumir(self, recursos_disponiveis):
        raise NotImplementedError

    def reproduzir(self):
        raise NotImplementedError

    def envelhecer(self):
        if self.quantidade <= 5:
            return

        chance_morte = 0.02  # 2% por mês

        mortes = 0
        for _ in range(self.quantidade):
            if random.random() < chance_morte:
                mortes += 1

        mortes = min(mortes, self.quantidade)  # permite reduzir até 0
        self.quantidade -= mortes


# ============================================================
# HERBÍVOROS
# ============================================================
class Herbivoro(Animal):
    def __init__(self, nome, quantidade, consumo):
        super().__init__(nome, quantidade, consumo)
        self.idade = 0
        self.idade_max = random.randint(8, 12)

    def consumir(self, plantas_disponiveis):
        """
        consumo_total agora usa math.ceil para evitar truncamento a zero
        quando existem indivíduos com consumo fracionário.
        Retorna plantas_restantes (int).
        """
        # consumo total real esperado (arredondado pra cima)
        consumo_total = math.ceil(self.quantidade * self.consumo)
        plantas_restantes = max(0, int(plantas_disponiveis) - consumo_total)

        # se houve falta de plantas, calcular mortes
        if plantas_disponiveis < consumo_total and self.quantidade > 0:
            # déficit (float)
            deficit = (consumo_total - int(plantas_disponiveis))
            # amortecador que traduz déficit em mortes; mantive lógica similar,
            # mas com divisão mais precisa e ceil para assegurar efeito quando necessário
            amortecador = max(1, int(max(1, self.consumo) * 6))
            mortes = math.ceil(deficit / max(1, amortecador))

            # não remover mais do que existe
            mortes = min(mortes, self.quantidade)
            self.quantidade -= mortes

        return plantas_restantes

    def reproduzir(self):
        pares = self.quantidade // 2
        novos = 0
        taxa = 0.08  # <--- reduzido de 0.22 para 0.08
        for _ in range(pares):
            if random.random() <= taxa:
                novos += 1
        self.quantidade += novos

    def envelhecer(self):
        self.idade += 1
        if self.idade >= self.idade_max:
            self.quantidade = max(0, self.quantidade - 1)

# ============================================================
# CARNÍVOROS
# ============================================================
class Carnivoro(Animal):
    def consumir(self, herbivoros_disponiveis):
        """
        Retorna quantas presas foram comidas (inteiro).
        A aplicação da redução de população por fome é MUITO suave.
        """
        necessidade = int(self.quantidade * self.consumo)

        # eficiência de caça: nem sempre consome tudo que "precisa"
        eficiencia = 0.65  # 65% de sucesso médio
        presas_possiveis = int(herbivoros_disponiveis)
        presas_comidas = min(necessidade, presas_possiveis)
        presas_comidas = int(round(presas_comidas * eficiencia))

        # Fome leve: só remove 1 indivíduo quando déficit significativo
        if presas_comidas < necessidade and self.quantidade > 0:
            deficit = necessidade - presas_comidas
            # só penaliza se déficit >= 1 consumo individual
            if deficit >= max(1, int(self.consumo)):
                self.quantidade = max(0, self.quantidade - 1)

        return int(presas_comidas)

    def reproduzir(self):
        pares = self.quantidade // 2
        novos = 0
        taxa = 0.12
        for _ in range(pares):
            if random.random() <= taxa:
                novos += 1
        self.quantidade += novos
