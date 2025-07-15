import random


class Animal:
    def __init__(self, nome, quantidade, consumo):
        self.nome = nome
        self.quantidade = quantidade
        self.consumo = consumo

    def consumir(self, recursos_disponiveis):
        raise NotImplementedError

    def reproduzir(self):
        raise NotImplementedError

    def envelhecer(self):
        raise NotImplementedError


class Herbivoro(Animal):
    def consumir(self, plantas_disponiveis):
        consumo_total = self.quantidade * self.consumo
        return max(0, plantas_disponiveis - consumo_total)

    def reproduzir(self):
        pares = self.quantidade // 2
        novos_individuos = 0
        for _ in range(pares):
            if random.random() <= 0.4:
                novos_individuos += random.randint(1, 3)
        self.quantidade += novos_individuos

    def envelhecer(self):
        self.quantidade = max(0, self.quantidade - random.randint(0, 1))


class Carnivoro(Animal):
    def consumir(self, herbivoros_disponiveis):
        consumo_total = self.quantidade * self.consumo
        return min(consumo_total, herbivoros_disponiveis)

    def reproduzir(self):
        pares = self.quantidade // 2
        novos_individuos = 0
        for _ in range(pares):
            if random.random() <= 0.2:
                novos_individuos += 1
        self.quantidade += novos_individuos

    def envelhecer(self):
        self.quantidade = max(0, self.quantidade - random.randint(0, 1))
