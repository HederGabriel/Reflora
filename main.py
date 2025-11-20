import pygame
import sys
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


# --- CALLBACKS ---
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


def carregar_jogo():
    if sistema.carregar():
        mudar_estado("jogo")


# --- BOTÕES MENU ---
buttons_menu = [
    Button((SCREEN_W // 2 - 120, 220, 240, 50), "Jogar (Novo)", BIG, callback=lambda: mudar_estado("selec_bioma")),
    Button((SCREEN_W // 2 - 120, 290, 240, 50), "Carregar", BIG, callback=carregar_jogo),
    Button((SCREEN_W // 2 - 120, 360, 240, 50), "Sair", BIG, callback=lambda: sys.exit()),
]

# --- BOTÕES BIOMAS ---
labels = ["Amazônia", "Cerrado", "Pantanal", "Caatinga"]
buttons_bioma = []

button_width = 200
button_height = 50
spacing = 30  # espaço entre botões

total_width = len(labels) * button_width + (len(labels) - 1) * spacing
start_x = (SCREEN_W - total_width) // 2
y = 300

for i, lbl in enumerate(labels, start=1):
    x = start_x + (i - 1) * (button_width + spacing)
    buttons_bioma.append(
        Button((x, y, button_width, button_height), lbl, FONT, callback=lambda x=i: escolher_bioma(x))
    )


# --- DESCRIÇÕES DOS BIOMAS ---
desc_biomas = {
    1: [
        "Amazônia",
        "• Maior biodiversidade do mundo",
        "• Altas chuvas e grande vegetação",
        "• Herbívoros e carnívoros variados",
    ],
    2: [
        "Cerrado",
        "• Savana brasileira",
        "• Árvores baixas e vegetação resistente",
        "• Diversidade de mamíferos",
    ],
    3: [
        "Pantanal",
        "• Maior planície alagável",
        "• Muita água e grande fauna aquática",
        "• Forte presença de onças e capivaras",
    ],
    4: [
        "Caatinga",
        "• Bioma semiárido",
        "• Vegetação resistente à seca",
        "• Animais adaptados ao calor extremo",
    ],
}

# Botões SIM / NÃO na confirmação
button_sim = Button((SCREEN_W//2 - 140, 500, 120, 50), "SIM", BIG, callback=confirmar_bioma_final)
button_nao = Button((SCREEN_W//2 + 20, 500, 120, 50), "NÃO", BIG, callback=lambda: mudar_estado("selec_bioma"))


# ------------------ DESENHAR TELAS ------------------

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


def draw_jogo():
    e = sistema.ecossistema
    screen.fill((220, 255, 220))

    pygame.draw.rect(screen, (240, 240, 240), (0, 0, SCREEN_W, 80))
    centered_text(screen, f"{e.bioma} — Ano {e.ano} Mês {e.mes}", FONT, 30)
    centered_text(screen,
                  f"Plantas {e.plantas}  |  Herbívoros {sum(a.quantidade for a in e.herbivoros.values())}  |  Carnívoros {sum(a.quantidade for a in e.carnivoros.values())}",
                  FONT, 55)

    actions = [
        "Plantar Vegetação",
        "Introduzir Herbívoros",
        "Introduzir Carnívoros",
        "Não Fazer Nada",
        "Salvar",
        "Histórico"
    ]
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

    return rects


# ----------------- LOOP PRINCIPAL -----------------

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.MOUSEMOTION:
            if estado == "selec_bioma":
                for b in buttons_bioma: b.handle_event(ev)
            elif estado == "confirma_bioma":
                button_sim.handle_event(ev)
                button_nao.handle_event(ev)

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if estado == "menu":
                for b in buttons_menu: b.handle_event(ev)

            elif estado == "selec_bioma":
                for b in buttons_bioma: b.handle_event(ev)

            elif estado == "confirma_bioma":
                button_sim.handle_event(ev)
                button_nao.handle_event(ev)

            elif estado == "jogo":
                rects = draw_jogo()
                for r, act in rects:
                    if r.collidepoint(ev.pos):
                        if act == "Plantar Vegetação":
                            sistema.ecossistema.adicionar_elementos("plantas")
                        elif act == "Introduzir Herbívoros":
                            sistema.ecossistema.adicionar_elementos("herbivoros")
                        elif act == "Introduzir Carnívoros":
                            sistema.ecossistema.adicionar_elementos("carnivoros")
                        elif act == "Salvar":
                            sistema.salvar()
                        elif act == "Histórico":
                            estado = "historico"

                        sistema.adicionar_ao_historico()
                        sistema.ecossistema.simular_mes()

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                estado = "menu"

    if estado == "menu":
        draw_menu()
    elif estado == "selec_bioma":
        draw_selec_bioma()
    elif estado == "confirma_bioma":
        draw_confirma_bioma()
    elif estado == "jogo":
        draw_jogo()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
