import pygame
import sys
import os
import json
import random
from sistema import SistemaJogo

BLACK = (0, 0, 0)
GRAY = (200, 200, 200)


# --- Classe Button: criação e interação de botões ---
class Button:
    def __init__(self, rect, text, font, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.hover = False

    def draw(self, surf):
        color = (170, 170, 170) if self.hover else GRAY
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        text = self.font.render(self.text, True, BLACK)
        surf.blit(text, text.get_rect(center=self.rect.center))

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos) and self.callback:
                self.callback()


def centered_text(surf, text, font, y, color=BLACK):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(surf.get_width() // 2, y))
    surf.blit(img, rect)


# --- Inicialização do pygame e recursos principais ---
pygame.init()

SCREEN_W, SCREEN_H = 1000, 640
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Reflora — Pygame")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 20)
BIG = pygame.font.SysFont("Arial", 32)

# --- Instância do sistema de simulação do jogo ---
sistema = SistemaJogo()

# ------------------------------------------------------
# VARIÁVEIS GLOBAIS (originais + extras para slots/modal)
# ------------------------------------------------------
pagina = "menu"
estado_salvamento = None
estado_tutorial_origem = None
bioma_selecionado = None
buttons_saves = []
alerta_saves = False
alerta_salvo = False

tempo_alerta_salvo = 0
TEMPO_ALERTA = 2

input_nome_save = ""
digitando_nome_save = False

nome_save_atual = None
criando_novo_jogo = False

alerta_nome_vazio = False
alerta_nome_existente = False

nome_digitado_para_save = None

button_voltar_saves = Button(
    (SCREEN_W // 2 - 60, 550, 120, 50),
    "Voltar",
    FONT,
    callback=lambda: mudar_estado("menu")
)

# -----------------------
# Tutorial
# -----------------------
tutorial_ativo = False
tutorial_pagina = 0

tutorial_textos = [
    ["Bem-vindo ao REFLORA.", "Seu objetivo é manter o ecossistema em equilíbrio."],
    ["As plantas são a base de toda a vida.", "Sem plantas, os herbívoros morrem."],
    ["Os herbívoros dependem das plantas.", "População excessiva consome toda a vegetação."],
    ["Carnívoros controlam os herbívoros.", "Sem predadores, ocorre desequilíbrio."],
    ["Em cada turno você pode:", "• Plantar vegetação", "• Introduzir animais", "• Ou não fazer nada"],
    ["Mantenha plantas, herbívoros e carnívoros vivos por 5 anos."]
]
tutorial_origem = "menu"

# modal e slots
modal_ativo = False
modal_slot = None
slots = []
slots_sub = []

# histórico
historico_ativo = False
historico_saves = []  # lista de SlotSave para o histórico
scroll_historico = 0

# ------------------------------------------------------
# DELAY DO COLAPSO
# ------------------------------------------------------
DURACAO_COLAPSO_MS = 3000  # 3 segundos

# ------------------------------------------------------
# AUX: segurança ao desenhar jogo
# ------------------------------------------------------
def ecossistema_ok():
    return getattr(sistema, "ecossistema", None) is not None

# ------------------------------------------------------
# FUNÇÕES/CLASSES PARA SLOTS VISUAIS
# ------------------------------------------------------
# --- Classe SlotSave: cartões visuais de saves ---
class SlotSave:
    def __init__(self, x, y, w, h, dados, nome_arquivo, modo_substituir=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.dados = dados
        self.nome_arquivo = nome_arquivo
        self.hover = False
        self.modo_substituir = modo_substituir

        # botões internos (posicionados relativos)
        self.btn_carregar = Button((x+15, y+h-45, 100, 35), "Carregar", FONT, callback=self.on_carregar)
        self.btn_apagar = Button((x+135, y+h-45, 100, 35), "Excluir", FONT, callback=self.on_apagar)
        self.btn_substituir = Button((x+60, y+h-45, 140, 35), "Substituir", FONT, callback=self.on_substituir)

    def draw(self, screen):
        cor = (220, 220, 220) if not self.hover else (240, 240, 255)
        pygame.draw.rect(screen, cor, self.rect, border_radius=10)
        pygame.draw.rect(screen, (80,80,80), self.rect, 2, border_radius=10)

        if not self.dados:
            t = BIG.render("Slot Vazio", True, (80,80,80))
            screen.blit(t, t.get_rect(center=self.rect.center))
            return

        # título e informações
        t = BIG.render(self.dados.get("bioma","?"), True, (0,0,0))
        screen.blit(t, (self.rect.x + 10, self.rect.y + 10))
        y = self.rect.y + 60
        for linha in [
            f"Save: {self.nome_arquivo.replace('.json','')}" if self.nome_arquivo else "Save: -",
            f"Ano: {self.dados.get('ano', 0)}",
            f"Mês: {self.dados.get('mes', 0)}",
            f"Plantas: {self.dados.get('plantas', 0)}",
            f"Herbívoros: {sum(self.dados.get('herbivoros', {}).values())}",
            f"Carnívoros: {sum(self.dados.get('carnivoros', {}).values())}",
        ]:
            tt = FONT.render(linha, True, (0,0,0))
            screen.blit(tt, (self.rect.x + 10, y))
            y += 22

        if not self.modo_substituir:
            self.btn_carregar.draw(screen)
            self.btn_apagar.draw(screen)
        else:
            self.btn_substituir.draw(screen)

    def on_carregar(self):
        if self.dados and self.nome_arquivo:
            if sistema.carregar(self.nome_arquivo):
                global nome_save_atual, pagina
                nome_save_atual = self.nome_arquivo.replace('.json','')
                mudar_estado("jogo")

    def on_apagar(self):
        global modal_ativo, modal_slot
        modal_ativo = True
        modal_slot = self

    def on_substituir(self):
        # chama a função correta que faz tudo
        substituir_save(self.nome_arquivo)

    def handle_event(self, ev):
        # atualiza hover
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)

        # clique / interação
        if ev.type == pygame.MOUSEBUTTONDOWN:
            # clique no próprio cartão
            if self.rect.collidepoint(ev.pos):
                # se o slot ESTÁ VAZIO
                if not self.dados:
                    # Sempre iniciar um jogo novo corretamente
                    sistema.current_save_file = None
                    globals()['nome_save_atual'] = None

                    # se não há ecossistema ainda → fluxo normal de criar novo jogo
                    if not sistema.ecossistema:
                        mudar_estado("selec_bioma")
                        return

                    # já há jogo em andamento, apenas criar novo save para o jogo atual
                    iniciar_nome_save()
                    return

            # propaga evento para botões internos
            if not self.modo_substituir:
                self.btn_carregar.handle_event(ev)
                self.btn_apagar.handle_event(ev)
            else:
                self.btn_substituir.handle_event(ev)

# --- Carregamento e exibição dos slots de save ---
def carregar_slots(modo_sub=False):
    lista = []
    arquivos = [f for f in os.listdir() if f.endswith('.json') and f != "saveJogo.json"]
    arquivos = arquivos[:3]
    x_base = 80
    espacamento = 280
    for i in range(3):
        arq = arquivos[i] if i < len(arquivos) else None
        dados = None
        if arq and os.path.exists(arq):
            try:
                with open(arq, "r", encoding="utf-8") as f:
                    dados = json.load(f)
            except Exception:
                dados = None
        slot = SlotSave(x_base + i * espacamento, 150, 260, 350, dados, arq, modo_substituir=modo_sub)
        lista.append(slot)
    return lista

# ------------------------------------------------------
# Funções do fluxo de saves (mantidas e integradas)
# ------------------------------------------------------
def mudar_estado(e):
    global pagina
    pagina = e

def escolher_bioma(i):
    global bioma_selecionado
    bioma_selecionado = i
    mudar_estado("confirma_bioma")

def confirmar_bioma_final():
    global criando_novo_jogo, nome_save_atual, tutorial_origem

    criando_novo_jogo = True

    # limpar save anterior
    sistema.current_save_file = None
    nome_save_atual = None

    sistema.confirmar_bioma(sistema.escolher_bioma(bioma_selecionado))

    # define origem do tutorial para voltar ao jogo depois
    tutorial_origem = "novo_jogo"

    # abre a pergunta do tutorial
    perguntar_tutorial()

def abrir_lista_saves():
    global pagina, slots
    slots = carregar_slots(modo_sub=False)
    pagina = "lista_saves"

def abrir_substituir():
    global pagina, slots_sub, modal_ativo
    modal_ativo = False   # garantir que modal não bloqueie eventos aqui
    slots_sub = carregar_slots(modo_sub=True)
    pagina = "substituir_save"

def carregar_save(arq):
    global nome_save_atual
    if sistema.carregar(arq):
        nome_save_atual = arq.replace('.json', '')
        mudar_estado("jogo")

def apagar_save(arq):
    if os.path.exists(arq):
        os.remove(arq)
    abrir_lista_saves()

def iniciar_nome_save():
    global digitando_nome_save, input_nome_save, alerta_nome_existente, alerta_nome_vazio
    digitando_nome_save = True
    input_nome_save = ""
    alerta_nome_existente = False
    alerta_nome_vazio = False

# --- Lógica de salvar jogo ---
def salvar_jogo():
    global alerta_salvo, tempo_alerta_salvo, nome_save_atual

    # Caso 1: JÁ existe um save carregado → sobrescrever
    if sistema.current_save_file:
        sucesso = sistema.salvar()   # <----- sem nome!
        if sucesso:
            nome_save_atual = sistema.current_save_file.replace(".json", "")
            alerta_salvo = True
            tempo_alerta_salvo = pygame.time.get_ticks()
        return

    # Caso 2: NÃO existe save carregado → pedir nome
    iniciar_nome_save()

def salvar_jogo_com_enter():
    global nome_save_atual, input_nome_save, alerta_salvo
    global tempo_alerta_salvo, digitando_nome_save
    global alerta_nome_vazio, alerta_nome_existente


    # Proteção: não tenta salvar se não houver jogo
    if not ecossistema_ok():
        digitando_nome_save = False
        mudar_estado("selec_bioma")
        return

    alerta_nome_vazio = False
    alerta_nome_existente = False

    nome = input_nome_save.strip()
    if nome == "":
        alerta_nome_vazio = True
        return

    destino_rel = f"{nome}.json"
    destino_abs = os.path.abspath(destino_rel)
    arquivos_json = [f for f in os.listdir() if f.endswith(".json")]

    # tenta salvar
    sucesso = sistema.salvar(nome_save=nome)

    arquivos_json2 = [f for f in os.listdir() if f.endswith(".json")]

    if not sucesso:
        # limite de 3 saves -> abrir tela de substituição
        if sistema.save_limit_reached:
            global nome_digitado_para_save
            nome_digitado_para_save = nome  # <-- salva o nome digitado ANTES de abrir os slots

            digitando_nome_save = False
            abrir_substituir()
            return

        # nome já existe ou falha -> alerta
        alerta_nome_existente = True
        return

    # salvo com sucesso -> sincroniza nome e UI
    nome_save_atual = sistema.current_save_file.replace('.json', '') if sistema.current_save_file else nome
    alerta_salvo = True
    tempo_alerta_salvo = pygame.time.get_ticks()

    # reseta flags de input
    digitando_nome_save = False
    input_nome_save = ""

    # Atualiza slots e vai de volta ao jogo
    abrir_lista_saves()
    mudar_estado("jogo")

def sair_e_salvar():
    global alerta_salvo, tempo_alerta_salvo
    if nome_save_atual:
        sucesso = sistema.salvar(nome_save=nome_save_atual)
        if sistema.save_limit_reached:
            abrir_substituir()
            return
        if sucesso:
            alerta_salvo = True
            tempo_alerta_salvo = pygame.time.get_ticks()
            mudar_estado("menu")
            return
    iniciar_nome_save()

def substituir_save(alvo):
    global nome_save_atual, modal_ativo, modal_slot, slots_sub, nome_digitado_para_save


    tmp = "saveJogo.json"
    if not os.path.exists(tmp):
        abrir_substituir()
        return

    # nome que o usuário digitou antes de abrir a tela de substituir
    if not nome_digitado_para_save:
        # fallback: se não tivermos o nome, usar o nome do slot clicado
        nome_digitado = alvo.replace(".json", "")
    else:
        nome_digitado = nome_digitado_para_save

    novo_nome = f"{nome_digitado}.json"

    try:
        # 1) Se já existe um arquivo com o novo nome e ele NÃO é o slot clicado,
        #    removemos esse novo_nome para evitar duplicatas.
        if os.path.exists(novo_nome) and os.path.abspath(novo_nome) != os.path.abspath(alvo):
            os.remove(novo_nome)

        # 2) Remover o arquivo do slot clicado (alvo) — é o que o usuário escolheu para ser trocado
        if os.path.exists(alvo):
            os.remove(alvo)

        # 3) Mover o temporário para o novo nome (atomicamente)
        os.replace(tmp, novo_nome)

        # 4) Carregar o novo save e sincronizar pagina
        if sistema.carregar(novo_nome):
            sistema.current_save_file = novo_nome
            nome_save_atual = nome_digitado
            sistema.save_limit_reached = False
        else:
            abrir_lista_saves()
            return

    except Exception as e:
        sistema.save_limit_reached = False
        # tentar limpar temporário se ainda existir
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        abrir_lista_saves()
        return

    # Limpa modal/pagina e atualiza UI
    modal_ativo = False
    modal_slot = None

    # Recarrega slots após substituição
    try:
        slots = carregar_slots(modo_sub=False)
    except Exception:
        pass

    # ---- NOVO: marcar alerta de jogo salvo ----
    global alerta_salvo, tempo_alerta_salvo
    alerta_salvo = True
    tempo_alerta_salvo = pygame.time.get_ticks()


    mudar_estado("jogo")


def cancelar_substituir():
    global nome_save_atual, modal_ativo, modal_slot


    # 1. Se existe save temporário → carregar ele
    if os.path.exists("saveJogo.json"):
        if sistema.carregar("saveJogo.json"):
            nome_save_atual = None  # não há save associado
            sistema.current_save_file = None

        # 2. Apaga o save temporário
        try:
            os.remove("saveJogo.json")
        except Exception:
            pass
    # 3. Resetar flags
    sistema.save_limit_reached = False
    modal_ativo = False
    modal_slot = None

    # 4. Voltar ao jogo
    mudar_estado("jogo")

# botão cancelar na tela de substituição — declarado global para ser tratado no loop de eventos
btn_cancel_substituir = Button((SCREEN_W//2 - 100, 500, 200, 50), "Cancelar", BIG, callback=cancelar_substituir)

# ------------------------------------------------------
# BOTÕES (originais)
# ------------------------------------------------------
BUTTON_WIDTH, BUTTON_HEIGHT = 220, 60

button_sair_jogo = Button((SCREEN_W - 120, 20, 100, 40), "Sair", FONT, callback=lambda: mudar_estado("sair_confirm"))
button_sair_sim = Button((SCREEN_W//2 - BUTTON_WIDTH - 20, 300, BUTTON_WIDTH, BUTTON_HEIGHT), "Salvar e Sair", BIG, callback=sair_e_salvar)
button_sair_nao = Button((SCREEN_W//2 + 20, 300, BUTTON_WIDTH, BUTTON_HEIGHT), "Sair sem Salvar", BIG, callback=lambda: mudar_estado("menu"))
btn_carregar = Button((SCREEN_W // 2 - 120, 290, 240, 50), "Carregar", BIG, callback=abrir_lista_saves)

buttons_menu = [
    Button((SCREEN_W // 2 - 120, 220, 240, 50), "Jogar (Novo)", BIG, callback=lambda: mudar_estado("selec_bioma")),
    btn_carregar,
    Button((SCREEN_W // 2 - 120, 360, 240, 50), "Sair", BIG, callback=lambda: sys.exit()),
    Button((SCREEN_W // 2 - 120, 420, 240, 50), "Tutorial", BIG, callback=lambda: abrir_tutorial_menu()),
]

labels = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
buttons_bioma = []
button_width, button_height, spacing = 200, 50, 30
total_width = len(labels) * button_width + (len(labels) - 1) * spacing
start_x = (SCREEN_W - total_width) // 2
y_biomas = 300

for i, lbl in enumerate(labels, start=1):
    x = start_x + (i - 1) * (button_width + spacing)
    buttons_bioma.append(Button((x, y_biomas, button_width, button_height), lbl, FONT, callback=lambda x=i: escolher_bioma(x)))

button_cancelar_bioma = Button((SCREEN_W // 2 - 100, 500, 200, 50), "Cancelar", BIG, callback=lambda: mudar_estado("menu"))

button_fim_menu = Button(
    (SCREEN_W//2 - 120, 400, 240, 50),
    "Voltar ao Menu",
    BIG,
    callback=lambda: mudar_estado("menu")
)

# ------------------------------------------------------
# DESENHO DAS TELAS
# ------------------------------------------------------

# --- Renderização do tutorial ---
def draw_tutorial():
    # Fundo em degradê verde suave (padrão REFLORA)
    for y in range(SCREEN_H):
        cor = 210 + int(20 * (y / SCREEN_H))
        pygame.draw.line(screen, (cor, 250, cor), (0, y), (SCREEN_W, y))

    # Caixa central
    caixa_rect = pygame.Rect(100, 90, SCREEN_W - 200, 420)
    pygame.draw.rect(screen, (235, 255, 235), caixa_rect, border_radius=24)
    pygame.draw.rect(screen, (120, 200, 120), caixa_rect, 3, border_radius=24)

    # Título
    font_titulo = pygame.font.SysFont("Arial", 52, bold=True)
    titulo = font_titulo.render("TUTORIAL", True, (30, 100, 30))
    screen.blit(titulo, (SCREEN_W // 2 - titulo.get_width() // 2, 120))

    # Texto (lista de linhas)
    font_texto = pygame.font.SysFont("Arial", 28)
    linhas = tutorial_textos[tutorial_pagina]

    y_text = 210
    for linha in linhas:
        txt = font_texto.render(linha, True, (30, 90, 30))
        screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, y_text))
        y_text += 38

    # Indicador de página
    info = font_texto.render(f"{tutorial_pagina + 1} / {len(tutorial_textos)}", True, (60, 120, 60))
    screen.blit(info, (SCREEN_W // 2 - info.get_width() // 2, 520))

    # Botões padrão do jogo
    if tutorial_pagina > 0:
        Button((60, 540, 200, 50), "Voltar", BIG, callback=voltar_tutorial).draw(screen)

    Button((SCREEN_W - 260, 540, 200, 50), "Próximo", BIG, callback=proximo_tutorial).draw(screen)


def proximo_tutorial():
    global tutorial_pagina, tutorial_ativo

    tutorial_pagina += 1

    if tutorial_pagina >= len(tutorial_textos):
        tutorial_ativo = False
        tutorial_pagina = 0
        sair_tutorial()

def voltar_tutorial():
    global tutorial_pagina
    tutorial_pagina -= 1
    if tutorial_pagina < 0:
        tutorial_pagina = 0

def perguntar_tutorial():
    global pagina, estado_tutorial_origem
    estado_tutorial_origem = "novo_jogo"
    mudar_estado("pergunta_tutorial")

def pular_tutorial():
    global estado_tutorial_origem
    estado_tutorial_origem = None
    mudar_estado("jogo")

def iniciar_tutorial():
    mudar_estado("tutorial")

def draw_pergunta_tutorial():
    screen.fill((220, 250, 220))
    centered_text(screen, "Deseja ver o tutorial?", BIG, 200)

    btn_sim.draw(screen)
    btn_nao.draw(screen)

btn_prox = Button(
    (SCREEN_W - 260, 520, 200, 50),
    "Próximo",
    BIG,
    callback=proximo_tutorial
)

btn_voltar = Button(
    (60, 520, 200, 50),
    "Voltar",
    BIG,
    callback=voltar_tutorial
)

def abrir_tutorial_menu():
    global tutorial_origem
    tutorial_origem = "menu"
    mudar_estado("tutorial")

def sair_tutorial():
    global tutorial_origem

    if tutorial_origem == "menu":
        mudar_estado("menu")
    else:
        mudar_estado("jogo")

btn_sim = Button((SCREEN_W//2 - 120, 320, 100, 50), "Sim", BIG, callback=iniciar_tutorial)
btn_nao = Button((SCREEN_W//2 + 20, 320, 100, 50), "Não", BIG, callback=pular_tutorial)

# ------------------------------------------------------
# MODAL (confirmar exclusão)
# ------------------------------------------------------
def draw_modal():
    sombra = pygame.Surface((SCREEN_W, SCREEN_H))
    sombra.set_alpha(160)
    sombra.fill((0,0,0))
    screen.blit(sombra, (0,0))
    modal_rect = pygame.Rect(SCREEN_W//2-200, SCREEN_H//2-120, 400, 240)
    pygame.draw.rect(screen, (250,250,250), modal_rect, border_radius=10)
    centered_text(screen, "Excluir este save?", BIG, modal_rect.y + 40)
    btn_sim = Button((modal_rect.x + 60, modal_rect.y + 150, 100, 50), "Sim", BIG, callback=confirmar_exclusao)
    btn_nao = Button((modal_rect.x + 240, modal_rect.y + 150, 100, 50), "Não", BIG, callback=cancelar_exclusao)
    btn_sim.draw(screen)
    btn_nao.draw(screen)
    return [btn_sim, btn_nao]

def confirmar_exclusao():
    global modal_ativo, modal_slot, pagina
    if modal_slot and modal_slot.nome_arquivo:
        if os.path.exists(modal_slot.nome_arquivo):
            os.remove(modal_slot.nome_arquivo)
    modal_ativo = False
    modal_slot = None
    if pagina == "lista_saves":
        abrir_lista_saves()
    elif pagina == "substituir_save":
        abrir_substituir()

def cancelar_exclusao():
    global modal_ativo, modal_slot
    modal_ativo = False
    modal_slot = None


def draw_input_save():
    screen.fill((200, 200, 255))
    centered_text(screen, "Digite o nome do save e pressione ENTER", FONT, 100)
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_W//2 - 150, 200, 300, 50))
    t = FONT.render(input_nome_save, True, (0, 0, 0))
    screen.blit(t, (SCREEN_W//2 - 140, 210))
    if alerta_nome_vazio:
        warn = FONT.render("Por favor, digite um nome.", True, (200, 0, 0))
        screen.blit(warn, (SCREEN_W//2 - warn.get_width()//2, 270))
    if alerta_nome_existente:
        warn = FONT.render("Esse nome já existe. Escolha outro.", True, (200, 0, 0))
        screen.blit(warn, (SCREEN_W//2 - warn.get_width()//2, 300))

# --- Renderização do menu principal ---
def draw_menu():
    screen.fill((120, 200, 255))
    centered_text(screen, "REFLORA", BIG, 120)
    for b in buttons_menu:
        b.draw(screen)

def draw_selec_bioma():
    screen.fill((180, 255, 180))
    centered_text(screen, "Escolha um bioma", BIG, 100)
    for b in buttons_bioma:
        b.draw(screen)
    button_cancelar_bioma.draw(screen)

def draw_confirma_bioma():
    screen.fill((200, 240, 200))
    nomes = {
        1: ["Amazônia", "• Maior biodiversidade do mundo", "• Altas chuvas e grande vegetação", "• Herbívoros e carnívoros variados"],
        2: ["Cerrado", "• Savana brasileira", "• Árvores baixas e resistentes", "• Diversidade de mamíferos"],
        3: ["Pantanal", "• Maior planície alagável", "• Muita água e fauna aquática", "• Forte presença de onças e capivaras"],
        4: ["Caatinga", "• Bioma semiárido", "• Vegetação resistente", "• Animais adaptados ao calor extremo"],
    }
    if bioma_selecionado:
        info = nomes[bioma_selecionado]
        centered_text(screen, f"Confirmar bioma: {info[0]}", BIG, 80)
        y = 180
        for linha in info[1:]:
            centered_text(screen, linha, FONT, y)
            y += 40
        Button((SCREEN_W//2 - 140, 500, 120, 50), "SIM", BIG, callback=confirmar_bioma_final).draw(screen)
        Button((SCREEN_W//2 + 20, 500, 120, 50), "NÃO", BIG, callback=lambda: mudar_estado("selec_bioma")).draw(screen)
    else:
        centered_text(screen, "Nenhum bioma selecionado", FONT, 180)

def draw_lista_saves():
    # desenha slots
    screen.fill((150, 180, 200))
    centered_text(screen, "Saves Encontrados", BIG, 60)
    if not slots:
        t = FONT.render("Você não tem nenhum save.", True, (255, 0, 0))
        screen.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H//2 - 20))
        button_voltar_saves.draw(screen)
        return
    for s in slots:
        s.draw(screen)
    button_voltar_saves.draw(screen)

def draw_substituir_save():
    screen.fill((255, 210, 180))
    centered_text(screen, "Limite de 3 saves atingido!", BIG, 40)
    centered_text(screen, "Escolha qual save deseja substituir:", FONT, 100)

    if not slots_sub:
        centered_text(screen, "Nenhum save encontrado para substituir.", FONT, 160)
        btn_cancel_substituir.draw(screen)
        return

    for s in slots_sub:
        s.draw(screen)

    # desenha o botão cancelar (global)
    btn_cancel_substituir.draw(screen)

def draw_sair_confirm():
    screen.fill((255, 220, 220))
    centered_text(screen, "Deseja salvar antes de sair?", BIG, 200)
    button_sair_sim.draw(screen)
    button_sair_nao.draw(screen)

def draw_jogo():
    global alerta_salvo
    screen.fill((220, 255, 220))
    if not ecossistema_ok():
        centered_text(screen, "Nenhum jogo carregado. Volte ao menu.", BIG, SCREEN_H//2 - 40)
        return []
    e = sistema.ecossistema
    pygame.draw.rect(screen, (240, 240, 240), (0, 0, SCREEN_W, 80))
    centered_text(screen, f"{e.bioma} — Ano {e.ano} Mês {e.mes}", FONT, 30)
    centered_text(screen, f"Plantas {e.plantas}  |  Herbívoros {sum(a.quantidade for a in e.herbivoros.values())}  |  Carnívoros {sum(a.quantidade for a in e.carnivoros.values())}", FONT, 55)
    actions = ["Plantar Vegetação", "Introduzir Herbívoros", "Introduzir Carnívoros", "Não Fazer Nada", "Salvar", "Histórico"]
    rects = []
    for i, act in enumerate(actions):
        r = pygame.Rect(40, 120 + i * 60, 260, 50)
        rects.append((r, act))
        pygame.draw.rect(screen, (190, 190, 190), r, border_radius=5)
        t = FONT.render(act, True, (0, 0, 0))
        screen.blit(t, t.get_rect(center=r.center))
    pygame.draw.rect(screen, (255, 255, 255), (350, 120, 600, 440))
    y = 140
    for nome, a in e.herbivoros.items():
        screen.blit(FONT.render(f"H - {nome}: {a.quantidade}", True, (0, 0, 0)), (360, y))
        y += 26
    y += 10
    for nome, a in e.carnivoros.items():
        screen.blit(FONT.render(f"C - {nome}: {a.quantidade}", True, (0, 0, 0)), (360, y))
        y += 26
    if alerta_salvo:
        if (pygame.time.get_ticks() - tempo_alerta_salvo) / 1000 < TEMPO_ALERTA:
            msg = BIG.render("Jogo salvo!", True, (0, 200, 0))
            screen.blit(msg, ((SCREEN_W - msg.get_width()) // 2, 580))
        else:
            alerta_salvo = False
    button_sair_jogo.draw(screen)
    return rects

# ------------------------------------------------------
# Historico
# ------------------------------------------------------

def draw_historico(scroll=0):
    """Desenha o histórico do save atual no estilo claro do Reflora, com textos centralizados e espaçamento extra."""
    # Fundo claro (igual draw_jogo)
    screen.fill((220, 255, 220))

    # Título
    font_titulo = pygame.font.SysFont("Arial", 48, bold=True)
    titulo = font_titulo.render("Histórico do Jogo", True, (0, 0, 0))
    screen.blit(titulo, (SCREEN_W // 2 - titulo.get_width() // 2, 20))

    # Botão voltar
    button_voltar_saves.draw(screen)

    # Fonte para histórico
    font = pygame.font.SysFont("Consolas", 26)
    padding_y = 8
    spacing = 10  # espaçamento mínimo entre cada ação
    line_height = font.get_height() + padding_y * 2 + spacing

    historico = getattr(sistema.ecossistema, "historico", [])

    if not historico:
        # Mensagem centralizada no meio da tela
        texto = font.render("Nenhuma ação registrada ainda.", True, (0, 0, 0))
        screen.blit(texto, ((SCREEN_W - texto.get_width()) // 2,
                            (SCREEN_H - texto.get_height()) // 2))
    else:
        y_inicio = 100 + scroll
        for i, linha in enumerate(historico):
            # Cor de fundo alternada
            bg_color = (245, 245, 245) if i % 2 == 0 else (235, 235, 235)

            # Retângulo arredondado
            rect = pygame.Rect(40, y_inicio, SCREEN_W - 80, font.get_height() + padding_y * 2)
            pygame.draw.rect(screen, bg_color, rect, border_radius=8)

            # Barra lateral colorida
            if "Plantas" in linha:
                barra_color = (180, 230, 180)
            elif "Herbívoros" in linha:
                barra_color = (180, 210, 255)
            elif "Carnívoros" in linha:
                barra_color = (255, 180, 180)
            else:
                barra_color = (255, 225, 180)

            pygame.draw.rect(screen, barra_color, (42, y_inicio + 5, 10, font.get_height() + padding_y * 2 - 10),
                             border_radius=5)

            # Renderizar texto centralizado no retângulo
            texto = font.render(linha, True, (0, 0, 0))
            screen.blit(texto, (SCREEN_W // 2 - texto.get_width() // 2,
                                y_inicio + padding_y))

            # Incrementa Y com line_height + espaçamento extra
            y_inicio += line_height

# ------------------------------------------------------
# Telas Finais
# ------------------------------------------------------
if 'floresta' not in globals():
    floresta = []

    for _ in range(90):  # mais árvores
        arvore = {
            "x": random.randint(-100, SCREEN_W + 100),
            "altura": random.randint(150, 300),
            "largura": random.randint(10, 22),
            "folha_w": random.randint(100, 180),
            "folha_h": random.randint(80, 150),
            "verde": random.randint(70, 140)
        }
        floresta.append(arvore)

    floresta.sort(key=lambda a: a["altura"])

def draw_floresta_fundo():
    chao = SCREEN_H   # começa exatamente do chão da tela
    # "base" verde para não deixar buracos
    pygame.draw.rect(screen, (170, 230, 170), (0, SCREEN_H - 220, SCREEN_W, 240))

    for a in floresta:
        tronco_cor = (90, 60, 30)
        folha_cor = (40, a["verde"], 40)

        # Tronco
        pygame.draw.rect(
            screen,
            tronco_cor,
            (a["x"], chao - a["altura"], a["largura"], a["altura"])
        )

        # Copa
        pygame.draw.ellipse(
            screen,
            folha_cor,
            (
                a["x"] - a["folha_w"] // 2,
                chao - a["altura"] - (a["folha_h"] // 2),
                a["folha_w"],
                a["folha_h"]
            )
        )

if 'folhas' not in globals():
    folhas = []
    TOTAL_FOLHAS = 12

    for _ in range(TOTAL_FOLHAS):
        folha = {
            "y": random.randint(-100, SCREEN_H),

            # Começa obrigatoriamente nas árvores
            "x": random.choice([
                random.randint(-60, 160),                 # área da árvore esquerda
                random.randint(SCREEN_W - 200, SCREEN_W)  # área da árvore direita
            ]),

            "vel": random.uniform(0.5, 2.2),
            "tam": random.randint(6, 14)
        }
        folhas.append(folha)

def draw_fim_vitoria():
    tronco_largura = 110
    tronco_x_dir = SCREEN_W - 130
    tronco_x_esq = -20

    # Fundo em degradê
    for y in range(SCREEN_H):
        cor = 200 + int(20 * (y / SCREEN_H))
        pygame.draw.line(screen, (cor, 255, cor), (0, y), (SCREEN_W, y))

    # Floresta no fundo (nova)
    draw_floresta_fundo()


    # Caixa (fica abaixo das árvores)
    faixa_rect = pygame.Rect(80, 100, SCREEN_W - 160, 300)
    pygame.draw.rect(screen, (240, 255, 240), faixa_rect, border_radius=20)
    pygame.draw.rect(screen, (100, 200, 100), faixa_rect, 4, border_radius=20)

    # Texto
    font_titulo = pygame.font.SysFont("Arial", 64, bold=True)
    titulo = font_titulo.render("PARABÉNS!", True, (40, 120, 40))
    screen.blit(titulo, (SCREEN_W//2 - titulo.get_width()//2, 170))

    font_msg = pygame.font.SysFont("Arial", 30)
    msg1 = font_msg.render("Você manteve o ecossistema saudável por 5 anos!", True, (0, 80, 0))
    screen.blit(msg1, (SCREEN_W//2 - msg1.get_width()//2, 260))

    msg2 = font_msg.render("A natureza está em equilíbrio graças a você.", True, (0, 100, 0))
    screen.blit(msg2, (SCREEN_W//2 - msg2.get_width()//2, 300))

    # Troncos (embaixo das folhas caindo)
    pygame.draw.rect(screen, (110, 70, 30), (tronco_x_dir, -50, tronco_largura, SCREEN_H + 100))
    pygame.draw.rect(screen, (110, 70, 30), (tronco_x_esq, -50, tronco_largura, SCREEN_H + 100))

    # → FOLHAS CAINDO (MEIO)
    for folha in folhas:
        folha["y"] += folha["vel"]
        folha["x"] += random.uniform(-0.3, 0.3)

        if folha["y"] > SCREEN_H:
            folha["y"] = random.randint(-100, -20)

            if random.choice([True, False]):
                folha["x"] = random.randint(-60, 160)
            else:
                folha["x"] = random.randint(SCREEN_W - 200, SCREEN_W)

        pygame.draw.ellipse(
            screen,
            (100, 180, 100),
            (folha["x"], folha["y"], folha["tam"] * 1.5, folha["tam"])
        )

    # → COPA DAS ÁRVORES (POR CIMA DE TUDO)
    # Direita
    pygame.draw.circle(screen, (50, 130, 50), (tronco_x_dir + 40, 40), 150)
    pygame.draw.circle(screen, (60, 150, 60), (tronco_x_dir + 120, 90), 170)
    pygame.draw.circle(screen, (70, 160, 70), (tronco_x_dir - 10, 140), 160)
    pygame.draw.circle(screen, (60, 140, 60), (tronco_x_dir + 60, 200), 170)

    # Esquerda
    pygame.draw.circle(screen, (50, 130, 50), (tronco_x_esq + 70, 40), 150)
    pygame.draw.circle(screen, (60, 150, 60), (tronco_x_esq - 20, 90), 170)
    pygame.draw.circle(screen, (70, 160, 70), (tronco_x_esq + 120, 140), 160)
    pygame.draw.circle(screen, (60, 140, 60), (tronco_x_esq + 40, 200), 170)

    # Botão
    button_fim_menu.rect.y = 470
    button_fim_menu.draw(screen)

def draw_fim_derrota():
    screen.fill((255, 200, 200))
    centered_text(screen, "Fim de Jogo", BIG, 150)
    centered_text(screen, "O ecossistema colapsou.", FONT, 250)
    button_fim_menu.draw(screen)


def draw_colapso():
    # Mostra o jogo normalmente
    draw_jogo()

    # Escurece a tela levemente
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    overlay.set_alpha(120)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    msg = BIG.render("O ecossistema está colapsando...", True, (255, 200, 200))
    screen.blit(msg, ((SCREEN_W - msg.get_width()) // 2, 300))

# ------------------------------------------------------
# LOOP PRINCIPAL
# ------------------------------------------------------

running = True

while running:

    # --------------------------------------------------
    # CAPTURA DE EVENTOS (mouse, teclado, janela, etc.)
    # --------------------------------------------------
    for ev in pygame.event.get():

        # Fechou a janela → encerra o jogo
        if ev.type == pygame.QUIT:
            running = False

        # =================================================
        # DIGITAÇÃO DO NOME DO SAVE
        # =================================================
        if digitando_nome_save and ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                salvar_jogo_com_enter()     # confirma o nome digitado
            elif ev.key == pygame.K_BACKSPACE:
                input_nome_save = input_nome_save[:-1]   # apaga caractere
            else:
                input_nome_save += ev.unicode            # adiciona caractere
            continue   # impede qualquer outro pagina de interferir

        # =================================================
        # MODAL ATIVO (bloqueia 100% dos outros eventos)
        # =================================================
        if modal_ativo:
            botoes_modal = draw_modal()     # redesenha modal
            for b in botoes_modal:
                b.handle_event(ev)          # só o modal recebe eventos
            continue

        # =================================================
        # EVENTOS ESPECÍFICOS POR pagina ATUAL
        # =================================================
        if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL):

            # -------------------------
            # pagina: MENU PRINCIPAL
            # -------------------------
            if pagina == "menu":
                for b in buttons_menu:
                    b.handle_event(ev)

            # -------------------------
            # pagina: PERGUNTA DO TUTORIAL
            # -------------------------
            elif pagina == "pergunta_tutorial":
                btn_sim.handle_event(ev)
                btn_nao.handle_event(ev)

            # -------------------------
            # pagina: TUTORIAL
            # -------------------------
            elif pagina == "tutorial":
                if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    btn_prox.handle_event(ev)
                    if tutorial_pagina > 0:
                        btn_voltar.handle_event(ev)

            # -------------------------
            # pagina: SELEÇÃO DE BIOMA
            # -------------------------
            elif pagina == "selec_bioma":
                for b in buttons_bioma:
                    b.handle_event(ev)
                button_cancelar_bioma.handle_event(ev)

            # -------------------------
            # pagina: CONFIRMAÇÃO DE BIOMA
            # -------------------------
            elif pagina == "confirma_bioma":
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    x, y = ev.pos
                    # Botão SIM
                    if SCREEN_W // 2 - 140 <= x <= SCREEN_W // 2 - 20 and 500 <= y <= 550:
                        confirmar_bioma_final()
                    # Botão NÃO
                    if SCREEN_W // 2 + 20 <= x <= SCREEN_W // 2 + 140 and 500 <= y <= 550:
                        mudar_estado("selec_bioma")

            # -------------------------
            # pagina: LISTA DE SAVES
            # -------------------------
            elif pagina == "lista_saves":
                for s in slots:
                    s.handle_event(ev)
                button_voltar_saves.handle_event(ev)

            # -------------------------
            # pagina: JOGO PRINCIPAL
            # -------------------------
            elif pagina == "jogo":
                rects = draw_jogo()    # Botões centrais da simulação
                button_sair_jogo.handle_event(ev)

                # Clique em ações de jogo
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    for r, act in rects:
                        if r.collidepoint(ev.pos):

                            # Segurança: se o ecossistema não existe, volta ao início
                            if not ecossistema_ok():
                                mudar_estado("selec_bioma")
                                break

                            eco = sistema.ecossistema

                            # As ações do jogo alteram o ecossistema
                            if act == "Plantar Vegetação":
                                aumento = random.randint(60, 120)
                                eco.plantas = min(eco.capacidade_plantas, eco.plantas + aumento)
                                sistema.adicionar_ao_historico()
                                eco.simular_mes()

                            elif act == "Introduzir Herbívoros":
                                for h in eco.herbivoros.values():
                                    h.quantidade += random.randint(3, 6)
                                sistema.adicionar_ao_historico()
                                eco.simular_mes()

                            elif act == "Introduzir Carnívoros":
                                for c in eco.carnivoros.values():
                                    c.quantidade += random.randint(1, 2)
                                sistema.adicionar_ao_historico()
                                eco.simular_mes()

                            elif act == "Não Fazer Nada":
                                sistema.adicionar_ao_historico()
                                eco.simular_mes()

                            elif act == "Salvar":
                                salvar_jogo()

                            elif act == "Histórico":
                                scroll_historico = 0
                                button_voltar_saves.callback = lambda: mudar_estado("jogo")
                                mudar_estado("historico")

                            # Após cada ação, verifica se houve fim de jogo
                            status_fim = eco.verificar_fim_jogo()
                            if status_fim:
                                if status_fim == "vitória":
                                    mudar_estado("fim_vitoria")
                                elif status_fim == "derrota":
                                    colapso_inicio = pygame.time.get_ticks()
                                    mudar_estado("colapso")

            # -------------------------
            # pagina: HISTÓRICO
            # -------------------------
            elif pagina == "historico":
                button_voltar_saves.handle_event(ev)
                if ev.type == pygame.MOUSEWHEEL:
                    scroll_historico += ev.y * 30     # rolagem suave

            # -------------------------
            # pagina: CONFIRMAÇÃO DE SAÍDA
            # -------------------------
            elif pagina == "sair_confirm":
                button_sair_sim.handle_event(ev)
                button_sair_nao.handle_event(ev)

            # -------------------------
            # pagina: SUBSTITUIR SAVES
            # -------------------------
            elif pagina == "substituir_save":
                for s in slots_sub:
                    s.handle_event(ev)
                btn_cancel_substituir.handle_event(ev)

            # -------------------------
            # pagina: TELAS FINAIS
            # -------------------------
            elif pagina in ("fim_vitoria", "fim_derrota"):
                button_fim_menu.handle_event(ev)

            # -------------------------
            # pagina: ANIMAÇÃO DE COLAPSO
            # -------------------------
            elif pagina == "colapso":
                pass    # eventos não interferem no colapso

    # =====================================================
    # TIMER DO COLAPSO (3 segundos antes da tela de derrota)
    # =====================================================
    if pagina == "colapso" and colapso_inicio:
        if pygame.time.get_ticks() - colapso_inicio >= DURACAO_COLAPSO_MS:
            colapso_inicio = None
            mudar_estado("fim_derrota")

    # =====================================================
    # DESENHO DA TELA DE ACORDO COM O pagina ATUAL
    # (somente UM draw_* por frame)
    # =====================================================

    if digitando_nome_save:
        draw_input_save()

    elif modal_ativo:
        if pagina == "lista_saves":
            draw_lista_saves()
        elif pagina == "substituir_save":
            draw_substituir_save()
        draw_modal()  # modal sempre fica por cima

    elif pagina == "menu":
        draw_menu()

    elif pagina == "pergunta_tutorial":
        draw_pergunta_tutorial()

    elif pagina == "tutorial":
        draw_tutorial()

    elif pagina == "selec_bioma":
        draw_selec_bioma()

    elif pagina == "confirma_bioma":
        draw_confirma_bioma()

    elif pagina == "lista_saves":
        draw_lista_saves()

    elif pagina == "jogo":
        draw_jogo()

    elif pagina == "historico":
        draw_historico(scroll=scroll_historico)

    elif pagina == "sair_confirm":
        draw_sair_confirm()

    elif pagina == "substituir_save":
        draw_substituir_save()

    elif pagina == "colapso":
        draw_colapso()

    elif pagina == "fim_vitoria":
        draw_fim_vitoria()

    elif pagina == "fim_derrota":
        draw_fim_derrota()

    # Atualiza frame e regula FPS
    pygame.display.update()
    clock.tick(60)

# Encerramento seguro
pygame.quit()
sys.exit()
