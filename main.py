# Pseudo codigo do jogo fodinha

INICIAR

IMPORTAR bibliotecas necessárias:
    socket
    Network
    Message
    random
    pickle
    os

INICIAR rede (Network)
INICIAR lista de jogadores (players)
INICIAR quantidade de vidas dos jogadores (12 vidas cada)
INICIAR rodada atual (1)
INICIAR número de cartas na rodada (13 cartas)

ENQUANTO número de jogadores com vida > 1:
    LIMPAR tela
    EMBARALHAR cartas (deck)
    
    DISTRIBUIR cartas para jogadores (conforme número de cartas na rodada)
    
    PARA cada jogador:
        PEDIR palpite (quantidade de jogadas que acredita fazer)
    
    INICIAR jogadas na rodada
    INICIAR jogador inicial (primeiro jogador à direita do embaralhador)
    
    PARA cada jogada na rodada:
        PARA cada jogador em ordem:
            JOGAR uma carta na mesa
        DETERMINAR vencedor da jogada (carta mais alta ganha)
        ATUALIZAR jogador inicial para a próxima jogada (vencedor da jogada)
    
    CALCULAR resultados da rodada:
    PARA cada jogador:
        COMPARAR palpite com jogadas feitas
        ATUALIZAR vidas do jogador (perder diferença entre palpite e jogadas feitas)
    
    ATUALIZAR número de cartas na rodada (diminuir para próxima rodada, ou aumentar após chegar a 1 carta)

EXIBIR vencedor (último jogador com vida)
FINALIZAR
