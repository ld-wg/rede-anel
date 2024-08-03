from utils import distribute_cards, wait_for_cards, send_bids, wait_and_respond_to_bids
from network import Network
import logging
import socket
import os

logging.basicConfig(level=logging.DEBUG)


def main():
    # Init network and players
    network = Network()
    address = socket.gethostbyname(socket.gethostname())
    local_player = network.get_chair(address)

    cards_in_round = 13

    while any(player.lives > 0 for player in network.players):
        os.system("clear")  # Clear the screen

        # Apenas o dealer envia as mensagens do tipo "shuffle" para entregar as cartas,
        # Outros players aguardam as mensagens, se forem destinatarios enviam "shuffle" com confirm="true" para o dealer enviar a proxima carta
        # Quando acabam as cartas, o dealer envia um "end_shuffle" para todos os jogadores, ordenados do anterior ate o proximo
        # Nessa ordem entao os players param de esperar por mensagem "shuffle", garantindo que nenhuma mensagem pare de circular caso algum player pare de escutar antes da hora

        if local_player.dealer:
            distribute_cards(local_player, network, cards_in_round)
        else:
            wait_for_cards(local_player, network)

        print(f"Player {local_player.ip} successfuly exited distribute cards")

        # Novamente apenas o dealer ira enviar as mensagens do tipo "bid" para cada outro jogador.
        # Outros players aguardam a mensagem, se forem destinararios, colocam a "bid" e confirm=true na mensagem, e enviam para o dealer
        # Quandos acabarem os players, o dealer envia uma mensagem para todos com "end_bid", ordenados do anterior ate o proximo
        # Nessa ordem entao os players param de esperar por mensagem "bid", garantindo que nenhuma mensagem pare de circular caso algum player pare de escutar antes da hora
        if local_player.dealer:
            send_bids(network, cards_in_round)
        else:
            wait_and_respond_to_bids(local_player, network, cards_in_round)

        print(f"Player {local_player.ip} successfuly exited collecting bids")

        # while True:
        #     raw_data = network.socket.recv(4096)
        #     network.socket.sendto(raw_data, network.get_ip_port(local_player.next))

        network.pass_dealer()


if __name__ == "__main__":
    main()
