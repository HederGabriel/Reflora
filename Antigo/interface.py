import os
import msvcrt


def limpar_console():
    os.system("cls")


def aguardar_enter_inicial():
    while True:
        tecla = msvcrt.getch()
        if tecla == b'\r':
            break


def aguardar_enter(mensagem="Pressione Enter para continuar..."):
    print(mensagem)
    while True:
        tecla = msvcrt.getch()
        if tecla == b'\r':
            break


def capturar_tecla_numerica():
    while True:
        tecla = msvcrt.getch()
        if tecla in [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']:
            return int(tecla.decode())
        else:
            print("\nTecla inválida. Tente novamente.")


def exibir_tela_inicial():
    limpar_console()
    print("""
    ╔══════════════════════════════════════════════╗
    ║                   REFLORA!                   ║
    ╚══════════════════════════════════════════════╝
    ╔══════════════════════════════════════════════╗
    ║          Pressione Enter para Jogar          ║
    ╚══════════════════════════════════════════════╝
    """)
    aguardar_enter_inicial()


def exibir_tutorial():
    limpar_console()
    print("""
    ╔═════════════════════════════════════════════╗
    ║            BEM-VINDO AO REFLORA!            ║
    ╚═════════════════════════════════════════════╝

    Seu objetivo é restaurar e manter o equilíbrio de um bioma por 50 anos!
    Escolha um dos biomas para iniciar sua jornada:

    🌳 1. AMAZÔNIA  
        • Um bioma com uma vegetação abundante e uma grande diversidade de herbívoros.

    🔥 2. CERRADO  
        • Um bioma de savana tropical com vegetação adaptada e rica biodiversidade.

    🐊 3. PANTANAL  
        • Um ecossistema alagado com uma fauna diversa e vegetação exuberante.

    🌵 4. CAATINGA  
        • Um bioma semiárido com vegetação resistente e uma proporção maior de carnívoros.

    ╔════════════════════════════════════════════╗
    ║                COMO JOGAR                  ║
    ╚════════════════════════════════════════════╝

    A cada rodada, você terá 4 escolhas:
    1 PLANTAR PLANTAS - Adicione vegetação ao bioma.
    2 INTRODUZIR HERBÍVOROS - Adicione animais herbívoros.
    3 INTRODUZIR CARNÍVOROS - Adicione predadores.
    4 NÃO FAZER NADA - Avance o tempo sem ações.

    🌟 O jogo avança em meses. A cada 60 meses (5 anos), você decide:
        • Continuar ou encerrar a simulação.

    ⚠️ CONDIÇÕES DE DERROTA:
        • Todas as plantas morrem. 🌱❌
        • Todos os animais morrem. 🐾❌

    🏆 CONDIÇÃO DE VITÓRIA:
        • O ecossistema se mantém equilibrado até o MÊS 600 (50 anos)!

    ╔════════════════════════════════════════════╗
    ║                 BOA SORTE!                 ║
    ║   Equilibre a natureza e divirta-se! 🌳    ║
    ╚════════════════════════════════════════════╝
    """)
    aguardar_enter()


def exibir_quantitativo(ecossistema):
    """
    Exibe o estado atual do ecossistema (plantas, herbívoros e carnívoros).
    """
    limpar_console()
    print(f"Ano: {ecossistema.ano}, Mês: {ecossistema.mes}")
    print(f"Plantas: {ecossistema.plantas}")
    print(f"Herbívoros: {sum(animal.quantidade for animal in ecossistema.herbivoros.values())}")
    print(f"Carnívoros: {sum(animal.quantidade for animal in ecossistema.carnivoros.values())}")


def exibir_historico(historico_jogo):
    if not historico_jogo:
        print("\nNenhum registro no histórico.")
        return

    print("\nHistórico de jogos:")
    for i, registro in enumerate(historico_jogo, 1):
        print(f"Registro: {i}")
        print(registro)


def decisao_usuario(ecossistema):
    while True:
        limpar_console()
        exibir_quantitativo(ecossistema)

        print("\nEscolha uma ação:")
        print("1. Plantar mais vegetação")
        print("2. Introduzir mais herbívoros")
        print("3. Introduzir mais carnívoros")
        print("4. Não fazer nada")
        print("5. Ver status do ecossistema")

        print("Escolha uma opção (1-5): ", end="", flush=True)
        opcao = capturar_tecla_numerica()

        if opcao == 1:
            ecossistema.adicionar_elementos("plantas")
            return True
        elif opcao == 2:
            ecossistema.adicionar_elementos("herbivoros")
            return True
        elif opcao == 3:
            ecossistema.adicionar_elementos("carnivoros")
            return True
        elif opcao == 4:
            return True
        elif opcao == 5:
            limpar_console()
            ecossistema.exibir_status()
            aguardar_enter("Pressione Enter para continuar...")
            return False
        else:
            print("\nOpção inválida. Digite um número entre 1 e 5.")
            aguardar_enter("\nPressione Enter para tentar novamente...")