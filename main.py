import pygame
import sys
import os
import json
from interface_pygame import Button, centered_text
from sistema import SistemaJogo

pygame.init()

SCREEN_W, SCREEN_H = 1000, 640
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Reflora — Pygame")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 20)
BIG = pygame.font.SysFont("Arial", 32)

sistema = SistemaJogo()

estado = "menu"
bioma_selecionado = None
buttons_saves = []
button_voltar_saves = Button((SCREEN_W // 2 - 60, 550, 120, 50), "Voltar", FONT, callback=lambda: mudar_estado("menu"))


# --- CALLBACKS ---
def mudar_estado(e):
    global estado
    estado = e

def ha_saves():
    # verifica se existe pelo menos um saveX.json
    return any(f.startswith("save") and f.endswith(".json") for f in os.listdir() if os.path.isfile(f))

def escolher_bioma(i):
    global bioma_selecionado, estado
    bioma_selecionado = i
    estado = "confirma_bioma"

def confirmar_bioma_final():
    sistema.confirmar_bioma(sistema.escolher_bioma(bioma_selecionado))
    mudar_estado("jogo")

def carregar_jogo():
    if sistema.carregar():
        mudar_estado("jogo")

def abrir_lista_saves():
    global estado, buttons_saves
    saves = [f for f in os.listdir() if f.startswith("save") and f.endswith(".json")]
    if not saves:
        return

    # Limita até 3 saves
    saves = saves[:3]

    buttons_saves = []

    # Centraliza verticalmente na tela
    bloco_altura = 90
    bloco_largura = 400
    spacing = 30
    total_height = len(saves) * (bloco_altura + spacing) - spacing
    start_y = (SCREEN_H - total_height) // 2

    for idx, arquivo in enumerate(saves):
        nome = arquivo
        bloco_x = (SCREEN_W - bloco_largura) // 2
        bloco_y = start_y + idx * (bloco_altura + spacing)

        # Botões Carregar e Apagar dentro do bloco
        btn_load = Button((bloco_x + 40, bloco_y + 50, 150, 40), "Carregar", FONT, callback=lambda a=arquivo: carregar_save(a))
        btn_del = Button((bloco_x + 220, bloco_y + 50, 150, 40), "Apagar", FONT, callback=lambda a=arquivo: apagar_save(a))

        buttons_saves.append((btn_load, btn_del, nome, bloco_x, bloco_y))

    estado = "lista_saves"

def carregar_save(arq):
    if sistema.carregar(arq):
        mudar_estado("jogo")

def apagar_save(arq):
    if os.path.exists(arq):
        os.remove(arq)
    mudar_estado("menu")

def salvar_jogo():
    """
    Salva o jogo atual.
    Se carregou um save, sobrescreve.
    Se não, cria novo save, respeitando limite de 3.
    """
    sistema.salvar()


# --- BOTÕES MENU ---
btn_carregar = Button((SCREEN_W // 2 - 120, 290, 240, 50), "Carregar", BIG, callback=abrir_lista_saves)

buttons_menu = [
    Button((SCREEN_W // 2 - 120, 220, 240, 50), "Jogar (Novo)", BIG, callback=lambda: mudar_estado("selec_bioma")),
    btn_carregar,
    Button((SCREEN_W // 2 - 120, 360, 240, 50), "Sair", BIG, callback=lambda: sys.exit()),
]

# --- BOTÕES BIOMAS ---
labels = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
buttons_bioma = []

button_width = 200
button_height = 50
spacing = 30
total_width = len(labels) * button_width + (len(labels) - 1) * spacing
start_x = (SCREEN_W - total_width) // 2
y_biomas = 300

for i, lbl in enumerate(labels, start=1):
    x = start_x + (i - 1) * (button_width + spacing)
    buttons_bioma.append(
        Button((x, y_biomas, button_width, button_height), lbl, FONT, callback=lambda x=i: escolher_bioma(x))
    )

# --- DESCRIÇÕES DOS BIOMAS ---
desc_biomas = {
    1: ["Amazônia", "• Maior biodiversidade do mundo", "• Altas chuvas e grande vegetação", "• Herbívoros e carnívoros variados"],
    2: ["Cerrado", "• Savana brasileira", "• Árvores baixas e vegetação resistente", "• Diversidade de mamíferos"],
    3: ["Pantanal", "• Maior planície alagável", "• Muita água e grande fauna aquática", "• Forte presença de onças e capivaras"],
    4: ["Caatinga", "• Bioma semiárido", "• Vegetação resistente à seca", "• Animais adaptados ao calor extremo"],
}

# Botões SIM / NÃO na confirmação
button_sim = Button((SCREEN_W//2 - 140, 500, 120, 50), "SIM", BIG, callback=confirmar_bioma_final)
button_nao = Button((SCREEN_W//2 + 20, 500, 120, 50), "NÃO", BIG, callback=lambda: mudar_estado("selec_bioma"))

# Botão sair do jogo (sempre visível no canto superior direito)
button_sair_jogo = Button((SCREEN_W - 120, 20, 100, 40), "Sair", FONT, callback=lambda: mudar_estado("menu"))

# ------------------ DESENHAR TELAS ------------------
def draw_menu():
    screen.fill((120, 200, 255))
    centered_text(screen, "REFLORA", BIG, 120)
    if not ha_saves():
        btn_carregar.color_idle = (80, 80, 80)
        btn_carregar.color_hover = (80, 80, 80)
        btn_carregar.callback = None
    else:
        btn_carregar.color_idle = (200, 200, 200)
        btn_carregar.color_hover = (230, 230, 230)
        btn_carregar.callback = abrir_lista_saves
    for b in buttons_menu:
        b.draw(screen)

def draw_selec_bioma():
    screen.fill((180, 255, 180))
    centered_text(screen, "Escolha um bioma", BIG, 100)
    for b in buttons_bioma:
        b.draw(screen)

def draw_confirma_bioma():
    screen.fill((200, 240, 200))
    nome = desc_biomas[bioma_selecionado][0]
    centered_text(screen, f"Confirmar bioma: {nome}", BIG, 80)
    y = 180
    for linha in desc_biomas[bioma_selecionado][1:]:
        centered_text(screen, linha, FONT, y)
        y += 40
    button_sim.draw(screen)
    button_nao.draw(screen)

def draw_lista_saves():
    screen.fill((150, 180, 200))
    centered_text(screen, "Saves Encontrados", BIG, 100)

    for load, delete, nome, bloco_x, bloco_y in buttons_saves:
        # Bloco de fundo
        bloco_altura = 90
        bloco_largura = 400
        pygame.draw.rect(screen, (200, 200, 200), (bloco_x, bloco_y, bloco_largura, bloco_altura), border_radius=8)

        # Nome do save (sem ".json") centralizado
        nome_limpo = nome.replace(".json", "")
        t = FONT.render(nome_limpo, True, (0, 0, 0))
        screen.blit(t, t.get_rect(center=(bloco_x + bloco_largura // 2, bloco_y + 20)))

        # Ajusta posição dos botões
        load.rect.topleft = (bloco_x + 40, bloco_y + 50)
        delete.rect.topleft = (bloco_x + 220, bloco_y + 50)

        # Desenha os botões
        load.draw(screen)
        delete.draw(screen)

    # Botão voltar centralizado abaixo dos blocos
    button_voltar_saves.rect.topleft = (SCREEN_W // 2 - 60, bloco_y + bloco_altura + 40)
    button_voltar_saves.draw(screen)

def draw_jogo():
    e = sistema.ecossistema
    screen.fill((220, 255, 220))

    pygame.draw.rect(screen, (240, 240, 240), (0, 0, SCREEN_W, 80))
    centered_text(screen, f"{e.bioma} — Ano {e.ano} Mês {e.mes}", FONT, 30)
    centered_text(screen,
                  f"Plantas {e.plantas}  |  Herbívoros {sum(a.quantidade for a in e.herbivoros.values())}  |  Carnívoros {sum(a.quantidade for a in e.carnivoros.values())}",
                  FONT, 55)

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

    button_sair_jogo.draw(screen)
    return rects

# ----------------- LOOP PRINCIPAL -----------------
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.MOUSEMOTION:
            if estado == "selec_bioma":
                for b in buttons_bioma:
                    b.handle_event(ev)
            elif estado == "confirma_bioma":
                button_sim.handle_event(ev)
                button_nao.handle_event(ev)
            elif estado == "lista_saves":
                for save_data in buttons_saves:  # percorre todos os saves
                    load, delete, _, _, _ = save_data
                    load.handle_event(ev)
                    delete.handle_event(ev)
                button_voltar_saves.handle_event(ev)  # trata o botão voltar
            elif estado == "menu":
                for b in buttons_menu:
                    b.handle_event(ev)
            elif estado == "jogo":
                for r, _ in []:
                    pass
                button_sair_jogo.handle_event(ev)

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if estado == "selec_bioma":
                for b in buttons_bioma:
                    b.handle_event(ev)
            elif estado == "confirma_bioma":
                button_sim.handle_event(ev)
            elif estado == "lista_saves":
                for save_data in buttons_saves:  # percorre todos os saves
                    load, delete, _, _, _ = save_data
                    load.handle_event(ev)
                    delete.handle_event(ev)
                button_voltar_saves.handle_event(ev)  # trata o botão voltar
            elif estado == "menu":
                for b in buttons_menu:
                    b.handle_event(ev)
            elif estado == "jogo":
                rects = draw_jogo()
                for r, act in rects:
                    if r.collidepoint(ev.pos):
                        if act == "Plantar Vegetação":
                            sistema.ecossistema.adicionar_elementos("plantas")
                            sistema.adicionar_ao_historico()
                            sistema.ecossistema.simular_mes()
                        elif act == "Introduzir Herbívoros":
                            sistema.ecossistema.adicionar_elementos("herbivoros")
                            sistema.adicionar_ao_historico()
                            sistema.ecossistema.simular_mes()
                        elif act == "Introduzir Carnívoros":
                            sistema.ecossistema.adicionar_elementos("carnivoros")
                            sistema.adicionar_ao_historico()
                            sistema.ecossistema.simular_mes()
                        elif act == "Não Fazer Nada":
                            sistema.adicionar_ao_historico()
                            sistema.ecossistema.simular_mes()
                        elif act == "Salvar":
                            salvar_jogo()  # apenas salva, sem alterar ecossistema
                        elif act == "Histórico":
                            estado = "historico"
                button_sair_jogo.handle_event(ev)

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                estado = "menu"

    # Desenho das telas
    if estado == "menu":
        draw_menu()
    elif estado == "selec_bioma":
        draw_selec_bioma()
    elif estado == "confirma_bioma":
        draw_confirma_bioma()
    elif estado == "lista_saves":
        draw_lista_saves()
    elif estado == "jogo":
        draw_jogo()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
