from ecossistema import Ecossistema
from interface import exibir_quantitativo, decisao_usuario, capturar_tecla_numerica, aguardar_enter, exibir_historico, \
    limpar_console

historico_jogo = []


def adicionar_ao_historico(ecossistema):
    historico_jogo.append(
        f"Ano: {ecossistema.ano}, Mês: {ecossistema.mes}\n"
        f"Plantas: {ecossistema.plantas}\n"
        f"Herbívoros: {sum(animal.quantidade for animal in ecossistema.herbivoros.values())}\n"
        f"Carnívoros: {sum(animal.quantidade for animal in ecossistema.carnivoros.values())}\n"
    )


def escolher_bioma():
    while True:
        limpar_console()
        print("Escolha um bioma:")
        print("1. Amazônia")
        print("2. Cerrado")
        print("3. Pantanal")
        print("4. Caatinga")
        print("Escolha um bioma (1-4): ", end="", flush=True)
        bioma = capturar_tecla_numerica()
        if bioma in [1, 2, 3, 4]:
            return ["Amazônia", "Cerrado", "Pantanal", "Caatinga"][bioma - 1]
        else:
            print("\nOpção inválida, tente novamente.")
            aguardar_enter()


def confirmar_bioma(bioma):
    while True:  # Loop até que o usuário escolha 1 ou 2
        limpar_console()
        ecossistema = Ecossistema(bioma)
        print(f"Bioma selecionado: {bioma}")
        print(f"Quantidade inicial de plantas: {ecossistema.plantas}")
        print("Herbívoros:")
        for nome, animal in ecossistema.herbivoros.items():
            print(f"  {nome}: {animal.quantidade}")
        print("Carnívoros:")
        for nome, animal in ecossistema.carnivoros.items():
            print(f"  {nome}: {animal.quantidade}")
        print("Confirmar bioma? (1 - Sim, 2 - Não): ", end="", flush=True)
        confirmar = capturar_tecla_numerica()

        if confirmar in [1, 2]:  # Verifica se a opção é válida
            return ecossistema if confirmar == 1 else None
        else:
            print("\nOpção inválida. Digite 1 para Sim ou 2 para Não.")
            aguardar_enter("\nPressione Enter para tentar novamente...")


def verificar_continuacao(ecossistema):
    if ecossistema.ano % 5 == 0 and ecossistema.mes == 1:
        print(f"\nO jogo atingiu {ecossistema.ano} anos. Deseja continuar?")
        print("1. Sim")
        print("2. Não")
        print("Escolha uma opção (1-2): ", end="", flush=True)
        opcao = capturar_tecla_numerica()
        return opcao == 1
    return True


def iniciar_jogo():
    while True:
        bioma = escolher_bioma()
        ecossistema = confirmar_bioma(bioma)
        if ecossistema:
            break

    while True:
        exibir_quantitativo(ecossistema)
        adicionar_ao_historico(ecossistema)

        if all(animal.quantidade == 0 for animal in ecossistema.herbivoros.values()) and \
                all(animal.quantidade == 0 for animal in ecossistema.carnivoros.values()):
            print("\nTodos os animais foram extintos. Fim de Jogo.")
            break

        if ecossistema.plantas == 0:
            print("\nTodas as plantas morreram. Fim de Jogo.")
            break

        if not verificar_continuacao(ecossistema):
            break

        if decisao_usuario(ecossistema):
            ecossistema.simular_mes()

    while True:
        print("\nDeseja ver o histórico do jogo?")
        print("1. Sim")
        print("2. Não")
        print("Escolha uma opção (1-2): ", end="", flush=True)
        opcao_historico = capturar_tecla_numerica()

        if opcao_historico == 1:
            exibir_historico(historico_jogo)
            break
        elif opcao_historico == 2:
            break
        else:
            print("\nOpção inválida. Digite 1 para Sim ou 2 para Não.")
            aguardar_enter("\nPressione Enter para tentar novamente...")
            limpar_console()


def verificar_reiniciar():
    while True:  # Loop até que o usuário escolha uma opção válida
        limpar_console()
        print("\nDeseja jogar novamente?")
        print("1. Sim")
        print("2. Não")
        print("Escolha uma opção (1-2): ", end="", flush=True)
        escolha = capturar_tecla_numerica()

        if escolha == 1:
            historico_jogo.clear()
            limpar_console()
            return True
        elif escolha == 2:
            limpar_console()
            print("Obrigado por jogar! Até a próxima!")
            exit()
        else:
            print("\nOpção inválida. Digite 1 para Sim ou 2 para Não.")
            aguardar_enter("\nPressione Enter para tentar novamente...")
