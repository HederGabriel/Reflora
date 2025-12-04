# main.py — Unificado: versão original corrigida + slots visuais/substituição/modal
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

# ------------------------------------------------------
# VARIÁVEIS GLOBAIS (originais + extras para slots/modal)
# ------------------------------------------------------
estado = "menu"
estado_salvamento = None
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

# modal e slots
modal_ativo = False
modal_slot = None
slots = []
slots_sub = []

# ------------------------------------------------------
# AUX: segurança ao desenhar jogo
# ------------------------------------------------------
def ecossistema_ok():
    return getattr(sistema, "ecossistema", None) is not None

# ------------------------------------------------------
# FUNÇÕES/CLASSES PARA SLOTS VISUAIS
# ------------------------------------------------------
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
                global nome_save_atual, estado
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
            except Exception as e:
                print("Erro lendo save", arq, e)
                dados = None
        slot = SlotSave(x_base + i * espacamento, 150, 260, 350, dados, arq, modo_substituir=modo_sub)
        lista.append(slot)
    return lista

# ------------------------------------------------------
# Funções do fluxo de saves (mantidas e integradas)
# ------------------------------------------------------
def mudar_estado(e):
    global estado
    estado = e

def escolher_bioma(i):
    global bioma_selecionado
    bioma_selecionado = i
    mudar_estado("confirma_bioma")

def confirmar_bioma_final():
    global criando_novo_jogo
    criando_novo_jogo = True
    sistema.confirmar_bioma(sistema.escolher_bioma(bioma_selecionado))
    mudar_estado("jogo")

def abrir_lista_saves():
    global estado, slots
    slots = carregar_slots(modo_sub=False)
    estado = "lista_saves"

def abrir_substituir():
    global estado, slots_sub, modal_ativo
    modal_ativo = False   # garantir que modal não bloqueie eventos aqui
    slots_sub = carregar_slots(modo_sub=True)
    estado = "substituir_save"

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

    print("[DEBUG] salvar_jogo_com_enter() chamado. input_nome_save repr:", repr(input_nome_save))

    # Proteção: não tenta salvar se não houver jogo
    if not ecossistema_ok():
        print("[WARN] salvar_jogo_com_enter: sem ecossistema. Redirecionando para novo jogo.")
        digitando_nome_save = False
        mudar_estado("selec_bioma")
        return

    alerta_nome_vazio = False
    alerta_nome_existente = False

    nome = input_nome_save.strip()
    if nome == "":
        alerta_nome_vazio = True
        print("[WARN] nome vazio no salvar_jogo_com_enter")
        return

    # DEBUG antes do salvar
    destino_rel = f"{nome}.json"
    destino_abs = os.path.abspath(destino_rel)
    arquivos_json = [f for f in os.listdir() if f.endswith(".json")]
    print("DEBUG antes salvar -> nome:", nome, "destino_rel:", destino_rel, "arquivos:", arquivos_json, "current_save_file:", sistema.current_save_file)

    # tenta salvar
    sucesso = sistema.salvar(nome_save=nome)

    print("DEBUG apos salvar -> sucesso:", sucesso, "save_limit_reached:", sistema.save_limit_reached, "current:", sistema.current_save_file)
    arquivos_json2 = [f for f in os.listdir() if f.endswith(".json")]
    print("DEBUG arquivos apos salvar:", arquivos_json2)

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
    print("[INFO] salvar_jogo_com_enter: criado e sincronizado:", sistema.current_save_file)

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

    print("[DEBUG] substituir_save: iniciado para alvo:", alvo)

    tmp = "saveJogo.json"
    if not os.path.exists(tmp):
        print("[ERROR] substituir_save: tmp saveJogo.json não encontrado.")
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
            print(f"[DEBUG] substituir_save: removido arquivo com novo nome existente {novo_nome}")

        # 2) Remover o arquivo do slot clicado (alvo) — é o que o usuário escolheu para ser trocado
        if os.path.exists(alvo):
            os.remove(alvo)
            print(f"[DEBUG] substituir_save: removido arquivo do slot clicado {alvo}")

        # 3) Mover o temporário para o novo nome (atomicamente)
        os.replace(tmp, novo_nome)
        print(f"[DEBUG] substituir_save: saveJogo.json movido para {novo_nome}")

        # 4) Carregar o novo save e sincronizar estado
        if sistema.carregar(novo_nome):
            sistema.current_save_file = novo_nome
            nome_save_atual = nome_digitado
            sistema.save_limit_reached = False
            print(f"[DEBUG] substituir_save: carregado e sincronizado -> {novo_nome}")
        else:
            print("[ERROR] substituir_save: falha ao carregar o save substituído.")
            abrir_lista_saves()
            return

    except Exception as e:
        print("[ERROR] substituir_save: exceção durante substituição:", e)
        sistema.save_limit_reached = False
        # tentar limpar temporário se ainda existir
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        abrir_lista_saves()
        return

    # Limpa modal/estado e atualiza UI
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

    print("[DEBUG] substituir_save: finalizado com sucesso. Voltando ao jogo.")

    mudar_estado("jogo")


def cancelar_substituir():
    global nome_save_atual, modal_ativo, modal_slot

    print("[DEBUG] cancelar_substituir: iniciado")

    # 1. Se existe save temporário → carregar ele
    if os.path.exists("saveJogo.json"):
        print("[DEBUG] saveJogo encontrado. Carregando antes de apagar...")
        if sistema.carregar("saveJogo.json"):
            nome_save_atual = None  # não há save associado
            sistema.current_save_file = None

        # 2. Apaga o save temporário
        try:
            os.remove("saveJogo.json")
            print("[DEBUG] saveJogo.json removido.")
        except Exception as e:
            print("[DEBUG] erro ao remover saveJogo.json:", e)

    # 3. Resetar flags
    sistema.save_limit_reached = False
    modal_ativo = False
    modal_slot = None

    # 4. Voltar ao jogo
    print("[DEBUG] cancelar_substituir: finalizado. Voltando ao jogo.")
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
    global modal_ativo, modal_slot, estado
    if modal_slot and modal_slot.nome_arquivo:
        if os.path.exists(modal_slot.nome_arquivo):
            os.remove(modal_slot.nome_arquivo)
    modal_ativo = False
    modal_slot = None
    if estado == "lista_saves":
        abrir_lista_saves()
    elif estado == "substituir_save":
        abrir_substituir()

def cancelar_exclusao():
    global modal_ativo, modal_slot
    modal_ativo = False
    modal_slot = None

# ------------------------------------------------------
# DESENHO DAS TELAS (originais e atualizadas)
# ------------------------------------------------------
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
# LOOP PRINCIPAL
# ------------------------------------------------------
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        # DIGITAÇÃO DO SAVE
        if digitando_nome_save and ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                salvar_jogo_com_enter()
            elif ev.key == pygame.K_BACKSPACE:
                input_nome_save = input_nome_save[:-1]
            else:
                input_nome_save += ev.unicode
            continue

        # modal ativo: capturar botões do modal
        if modal_ativo:
            botoes_modal = draw_modal()
            for b in botoes_modal:
                b.handle_event(ev)
            continue

        # eventos por estado / tela
        if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            if estado == "menu":
                for b in buttons_menu:
                    b.handle_event(ev)
            elif estado == "selec_bioma":
                for b in buttons_bioma:
                    b.handle_event(ev)
                button_cancelar_bioma.handle_event(ev)
            elif estado == "confirma_bioma":
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    x, y = ev.pos
                    if SCREEN_W//2 - 140 <= x <= SCREEN_W//2 - 20 and 500 <= y <= 550:
                        confirmar_bioma_final()
                    if SCREEN_W//2 + 20 <= x <= SCREEN_W//2 + 140 and 500 <= y <= 550:
                        mudar_estado("selec_bioma")
            elif estado == "lista_saves":
                for s in slots:
                    s.handle_event(ev)
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
            elif estado == "substituir_save":
                for s in slots_sub:
                    s.handle_event(ev)
                # tratar o botão cancelar global (tem que receber eventos)
                btn_cancel_substituir.handle_event(ev)

    # DESENHO DAS TELAS
    if digitando_nome_save:
        draw_input_save()
    elif modal_ativo:
        # desenha tela de fundo da tela atual e modal por cima
        if estado == "lista_saves":
            draw_lista_saves()
        elif estado == "substituir_save":
            draw_substituir_save()
        draw_modal()
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
    elif estado == "substituir_save":
        draw_substituir_save()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
