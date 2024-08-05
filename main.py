from utils import (
    distribute_cards,
    finish_round,
    get_cards,
    wait_finish_round,
    wait_for_cards,
    send_bids,
    wait_and_respond_to_bids,
    wait_get_cards,
)
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
    loser = False
    winner = False
    counter = up_down_counter()

    while any(player.hp > 0 for player in network.players):
        cards_in_round = next(counter)

        print(f"You have {local_player.hp} HP")

        # Apenas o dealer envia as mensagens do tipo "shuffle" para entregar as cartas,
        # Outros players aguardam as mensagens, se forem destinatarios enviam "shuffle" com confirm="true" para o dealer enviar a proxima carta
        # Quando acabam as cartas, o dealer envia um "end_shuffle"

        if local_player.dealer:
            distribute_cards(local_player, network, cards_in_round)
        else:
            wait_for_cards(local_player, network)

        print(f"Player {local_player.ip} successfuly exited distribute cards")
        print(f"Your cards are: {local_player.cards}. Wait to bid.")

        # Novamente apenas o dealer ira enviar as mensagens do tipo "bid" para cada outro jogador.
        # Outros players aguardam a mensagem, se forem destinararios, colocam a "bid" e confirm=true na mensagem, e enviam para o dealer
        # Quandos acabarem os players, o dealer envia uma mensagem para todos com "end_bid"
        if local_player.dealer:
            send_bids(network, cards_in_round)
        else:
            wait_and_respond_to_bids(local_player, network, cards_in_round)

        print(f"Player {local_player.ip} successfuly exited collecting bids")

        if local_player.dealer:
            get_cards(network, cards_in_round)
        else:
            wait_get_cards(network, local_player)

        print(f"Player {local_player.ip} successfuly exited round")

        if local_player.dealer:
            finish_round(network)
        else:
            wait_finish_round(network, local_player)

        if local_player.hp == 0:
            loser = True
            break

        network.remove_dead_players()

        if len(network.players) == 1:
            winner = True
            break

        network.reset_players_for_new_round()
        network.pass_dealer()

    if loser:
        print("You lost!")
    if winner:
        print("You won!")


def up_down_counter():
    while True:  # Infinite loop to continuously repeat the pattern
        # Count down from 13 to 1
        for i in range(5, 0, -1):
            yield i
        # Count up from 2 to 13 (2 because 1 is already yielded in the countdown)
        for i in range(2, 6):
            yield i


if __name__ == "__main__":
    main()
