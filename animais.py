import random

class Animal:
    def __init__(self, nome, quantidade, consumo):
        """
        nome: string
        quantidade: int (indivíduos)
        consumo: float (unidades de presa/plantas por indivíduo por mês)
        """
        self.nome = nome
        self.quantidade = int(max(0, quantidade))
        self.consumo = float(consumo)

    def consumir(self, recursos_disponiveis):
        raise NotImplementedError

    def reproduzir(self):
        raise NotImplementedError

    def envelhecer(self):
        if self.quantidade <= 5:
            return

        # Mortalidade quase simbólica
        chance_morte = 0.02  # 2% por mês

        mortes = 0
        for _ in range(self.quantidade):
            if random.random() < chance_morte:
                mortes += 1

        # Garantir que não mata toda a população
        mortes = min(mortes, self.quantidade - 2)
        self.quantidade -= mortes


# ============================================================
# HERBÍVOROS
# ============================================================
class Herbivoro(Animal):
    def consumir(self, plantas_disponiveis):
        """
        Herbívoros consomem plantas. Retorna plantas restantes.
        Mortes por fome são muito suavizadas para evitar extinção rápida.
        """
        consumo_total = int(self.quantidade * self.consumo)

        plantas_restantes = max(0, int(plantas_disponiveis) - consumo_total)

        if plantas_disponiveis < consumo_total and self.quantidade > 0:
            deficit = consumo_total - int(plantas_disponiveis)

            # amortecador maior: 1 morte a cada (consumo * 6) de falta
            amortecador = max(1, int(max(1, self.consumo) * 6))
            mortes = max(1, deficit // amortecador)

            # não matar quase toda a população
            mortes = min(mortes, max(0, self.quantidade - 1))
            self.quantidade = max(0, self.quantidade - mortes)

        return plantas_restantes

    def reproduzir(self):
        pares = self.quantidade // 2
        novos = 0
        taxa = 0.22  # ligeiro aumento para recuperação
        for _ in range(pares):
            if random.random() <= taxa:
                novos += 1
        self.quantidade += novos

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
