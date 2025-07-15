from sistema import iniciar_jogo, verificar_reiniciar
from interface import exibir_tela_inicial, exibir_tutorial


def principal():
    exibir_tela_inicial()
    exibir_tutorial()
    iniciar_jogo()


if __name__ == "__main__":
    while True:
        principal()
        if not verificar_reiniciar():
            break
