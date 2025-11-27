import pygame
import sys
import os
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

# ------------------------------------------------------
# VARIÁVEIS GLOBAIS
# ------------------------------------------------------
estado = "menu"
bioma_selecionado = None
buttons_saves = []
alerta_saves = False
alerta_salvo = False
tempo_alerta_salvo = 0
TEMPO_ALERTA = 2
input_nome_save = ""
digitando_nome_save = False
nome_save_atual = None  # guarda o nome do save carregado ou salvo
button_voltar_saves = Button((SCREEN_W // 2 - 60, 550, 120, 50), "Voltar", FONT, callback=lambda: mudar_estado("menu"))

# ------------------------------------------------------
# CALLBACKS
# ------------------------------------------------------
def mudar_estado(e):
    global estado
    estado = e

def escolher_bioma(i):
    global bioma_selecionado, estado
    bioma_selecionado = i
    estado = "confirma_bioma"

def confirmar_bioma_final():
    sistema.confirmar_bioma(sistema.escolher_bioma(bioma_selecionado))
    mudar_estado("jogo")

def abrir_lista_saves():
    global estado, buttons_saves, alerta_saves
    saves = [f for f in os.listdir() if f.endswith(".json")]
    buttons_saves = []
    alerta_saves = False

    if saves:
        saves = saves[:10]
        bloco_altura, bloco_largura, spacing = 90, 400, 30
        total_height = len(saves) * (bloco_altura + spacing) - spacing
        start_y = (SCREEN_H - total_height) // 2

        for idx, arquivo in enumerate(saves):
            bloco_x = (SCREEN_W - bloco_largura) // 2
            bloco_y = start_y + idx * (bloco_altura + spacing)
            btn_load = Button((0, 0, 150, 40), "Carregar", FONT, callback=lambda a=arquivo: carregar_save(a))
            btn_del = Button((0, 0, 150, 40), "Apagar", FONT, callback=lambda a=arquivo: apagar_save(a))
            buttons_saves.append((btn_load, btn_del, arquivo, bloco_x, bloco_y))
    else:
        alerta_saves = True

    estado = "lista_saves"

def carregar_save(arq):
    global nome_save_atual
    if sistema.carregar(arq):
        nome_save_atual = arq.replace(".json", "")
        mudar_estado("jogo")
    else:
        print(f"Falha ao carregar {arq}. Arquivo não encontrado ou inválido.")

def apagar_save(arq):
    if os.path.exists(arq):
        os.remove(arq)
    abrir_lista_saves()

def iniciar_nome_save():
    global digitando_nome_save, input_nome_save
    digitando_nome_save = True
    input_nome_save = ""

def salvar_jogo():
    global alerta_salvo, tempo_alerta_salvo
    if nome_save_atual:
        sistema.salvar(nome_save=nome_save_atual)
        alerta_salvo = True
        tempo_alerta_salvo = pygame.time.get_ticks()
    else:
        iniciar_nome_save()

def salvar_jogo_com_enter():
    global alerta_salvo, tempo_alerta_salvo, digitando_nome_save, nome_save_atual, input_nome_save
    if input_nome_save.strip() == "":
        return
    nome_save_atual = input_nome_save.strip()
    sistema.salvar(nome_save=nome_save_atual)
    alerta_salvo = True
    tempo_alerta_salvo = pygame.time.get_ticks()
    digitando_nome_save = False

# ------------------------------------------------------
# BOTÕES MENU
# ------------------------------------------------------
btn_carregar = Button((SCREEN_W // 2 - 120, 290, 240, 50), "Carregar", BIG, callback=abrir_lista_saves)
buttons_menu = [
    Button((SCREEN_W // 2 - 120, 220, 240, 50), "Jogar (Novo)", BIG, callback=lambda: mudar_estado("selec_bioma")),
    btn_carregar,
    Button((SCREEN_W // 2 - 120, 360, 240, 50), "Sair", BIG, callback=lambda: sys.exit()),
]

# ------------------------------------------------------
# BOTÕES SELEÇÃO DE BIOMA
# ------------------------------------------------------
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

# ------------------------------------------------------
# DESCRIÇÕES DOS BIOMAS
# ------------------------------------------------------
desc_biomas = {
    1: ["Amazônia", "• Maior biodiversidade do mundo", "• Altas chuvas e grande vegetação", "• Herbívoros e carnívoros variados"],
    2: ["Cerrado", "• Savana brasileira", "• Árvores baixas e vegetação resistente", "• Diversidade de mamíferos"],
    3: ["Pantanal", "• Maior planície alagável", "• Muita água e grande fauna aquática", "• Forte presença de onças e capivaras"],
    4: ["Caatinga", "• Bioma semiárido", "• Vegetação resistente à seca", "• Animais adaptados ao calor extremo"],
}

button_sim = Button((SCREEN_W//2 - 140, 500, 120, 50), "SIM", BIG, callback=confirmar_bioma_final)
button_nao = Button((SCREEN_W//2 + 20, 500, 120, 50), "NÃO", BIG, callback=lambda: mudar_estado("selec_bioma"))

# ------------------------------------------------------
# TELA DE SAIR
# ------------------------------------------------------
BUTTON_WIDTH, BUTTON_HEIGHT = 220, 60
button_sair_jogo = Button((SCREEN_W - 120, 20, 100, 40), "Sair", FONT, callback=lambda: mudar_estado("sair_confirm"))
button_sair_sim = Button(
    (SCREEN_W//2 - BUTTON_WIDTH - 20, 300, BUTTON_WIDTH, BUTTON_HEIGHT),
    "Salvar e Sair",
    BIG,
    callback=lambda: (salvar_jogo(), mudar_estado("menu"))
)
button_sair_nao = Button((SCREEN_W//2 + 20, 300, BUTTON_WIDTH, BUTTON_HEIGHT), "Sair sem Salvar", BIG, callback=lambda: mudar_estado("menu"))

def draw_sair_confirm():
    screen.fill((255, 220, 220))
    centered_text(screen, "Deseja salvar antes de sair?", BIG, 200)
    button_sair_sim.draw(screen)
    button_sair_nao.draw(screen)

# ------------------------------------------------------
# DESENHO TELAS
# ------------------------------------------------------
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
    if not buttons_saves:
        t = FONT.render("Você não tem nenhum save.", True, (255, 0, 0))
        screen.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H//2 - 20))
        button_voltar_saves.rect.topleft = (SCREEN_W//2 - 60, SCREEN_H//2 + 20)
        button_voltar_saves.draw(screen)
        return
    for load, delete, nome, bloco_x, bloco_y in buttons_saves:
        pygame.draw.rect(screen, (200, 200, 200), (bloco_x, bloco_y, 400, 90), border_radius=8)
        nome_limpo = nome.replace(".json", "")
        t = FONT.render(nome_limpo, True, (0, 0, 0))
        screen.blit(t, t.get_rect(center=(bloco_x + 200, bloco_y + 20)))
        load.rect.topleft = (bloco_x + 40, bloco_y + 50)
        delete.rect.topleft = (bloco_x + 220, bloco_y + 50)
        load.draw(screen)
        delete.draw(screen)
    button_voltar_saves.rect.topleft = (SCREEN_W//2 - 60, bloco_y + 130)
    button_voltar_saves.draw(screen)

def draw_input_save():
    screen.fill((200, 200, 255))
    centered_text(screen, "Digite o nome do save e pressione ENTER", FONT, 100)
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_W//2 - 150, 200, 300, 50))
    t = FONT.render(input_nome_save, True, (0, 0, 0))
    screen.blit(t, (SCREEN_W//2 - 140, 210))

def draw_jogo():
    global alerta_salvo
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
    if alerta_salvo:
        if (pygame.time.get_ticks() - tempo_alerta_salvo) / 1000 < TEMPO_ALERTA:
            msg = BIG.render("Jogo salvo!", True, (0, 200, 0))
            screen.blit(msg, ((SCREEN_W - msg.get_width()) // 2, 580))
        else:
            alerta_salvo = False
    button_sair_jogo.draw(screen)
    return rects

# ------------------------------------------------------
# LOOP PRINCIPAL
# ------------------------------------------------------
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            if digitando_nome_save:
                continue

            if estado == "menu":
                for b in buttons_menu: b.handle_event(ev)
            elif estado == "selec_bioma":
                for b in buttons_bioma: b.handle_event(ev)
                button_cancelar_bioma.handle_event(ev)
            elif estado == "confirma_bioma":
                button_sim.handle_event(ev)
                button_nao.handle_event(ev)
            elif estado == "lista_saves":
                for load, delete, nome, x, y in buttons_saves:
                    load.handle_event(ev)
                    delete.handle_event(ev)
                button_voltar_saves.handle_event(ev)
            elif estado == "jogo":
                rects = draw_jogo()
                button_sair_jogo.handle_event(ev)
                if ev.type == pygame.MOUSEBUTTONDOWN:
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
                                salvar_jogo()
                            elif act == "Histórico":
                                pass
            elif estado == "sair_confirm":
                button_sair_sim.handle_event(ev)
                button_sair_nao.handle_event(ev)

        # Captura de teclado para digitar nome do save
        if digitando_nome_save and ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                salvar_jogo_com_enter()
            elif ev.key == pygame.K_BACKSPACE:
                input_nome_save = input_nome_save[:-1]
            else:
                input_nome_save += ev.unicode

    # DESENHO DAS TELAS
    if digitando_nome_save:
        draw_input_save()
    elif estado == "menu":
        draw_menu()
    elif estado == "selec_bioma":
        draw_selec_bioma()
    elif estado == "confirma_bioma":
        draw_confirma_bioma()
    elif estado == "lista_saves":
        draw_lista_saves()
    elif estado == "jogo":
        draw_jogo()
    elif estado == "sair_confirm":
        draw_sair_confirm()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
