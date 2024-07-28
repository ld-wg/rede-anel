import random
import pickle
from message import Message
from player import Player
from network import Network


def send_bids(network: Network, cards_in_round: int):
    input("Press a key to start collecting bids: ")
    dealer = network.find_dealer()
    # Para cada jogador, envia a mensagem de "bid" e aguarda confirmacao
    for player in network.players:
        if player.id == dealer.id:
            while bid == 0:
                bid = int(input(f"Insira seu palpite, de 1 a: {cards_in_round}: "))
                if bid < 1 or bid > cards_in_round:
                    print(f"Palpite invalido, precisa ser de 1 a: {cards_in_round}")
                    bid = 0
            dealer.set_bid(bid)  # Dealer directly receives the card
        else:
            # Cria a mensagem de lance inicial
            bid_message = pickle.dumps(Message(dealer.id, dealer.ip, player.ip, "bid"))
            network.socket.sendto(bid_message, network.get_ip_port(dealer.next))

            # Espera a resposta do lance do jogador
            while True:
                raw_data = network.socket.recv(4096)
                data = pickle.loads(raw_data)

                if data.dest == dealer.ip:
                    if data.type == "bid" and data.confirm == "true":
                        player.set_bid(data.play)
                        print(f"Bid received from {data.origin}: {data.play}")
                        break
                    else:
                        print(
                            f"Player {dealer.ip} was expecting type bid and confirm true, received {data.type} from {data.origin}"
                        )
                else:
                    network.socket.sendto(raw_data, network.get_ip_port(dealer.next))

                data = None

    # Após receber todos os lances, envia a mensagem de finalização de lance
    for player in network.get_reversed_ordered_players():
        end_bid_message = pickle.dumps(
            Message(dealer.id, dealer.ip, player.ip, "end_bid")
        )
        network.socket.sendto(end_bid_message, network.get_ip_port(dealer.next))


def wait_and_respond_to_bids(
    local_player: Player, network: Network, cards_in_round: int
):
    while True:
        raw_data = network.socket.recv(4096)
        data = Message(pickle.loads(raw_data))

        if data:
            if data.dest == local_player.ip:
                if data.type == "bid":
                    # Jogador recebe o lance e envia sua resposta
                    while bid == 0:
                        bid = int(
                            input(f"Insira seu palpite, de 1 a: {cards_in_round}: ")
                        )
                        if bid < 1 or bid > cards_in_round:
                            print(
                                f"Palpite invalido, precisa ser de 1 a: {cards_in_round}"
                            )
                            bid = 0

                    response_message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "bid",
                        bid,
                        "true",
                    )
                    network.socket.sendto(
                        pickle.dumps(response_message),
                        network.get_ip_port(local_player.next),
                    )

                elif data.type == "end_bid":
                    break  # Sai do loop após confirmar o fim do lance
                else:
                    print(
                        f"Player {local_player.ip} was expecting type bid or end_bid, received {data.type} from {data.origin}"
                    )

            else:
                # Passa a mensagem adiante se não for destinada ao jogador local
                network.socket.sendto(raw_data, network.get_ip_port(local_player.next))

        data = None


def wait_for_cards(local_player: Player, network: Network):
    while True:
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        if data:
            if data.dest == local_player.ip:
                if data.type == "shuffle":
                    local_player.receive_card(data.play[0])
                    message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "confirm_shuffle",
                        "",
                        "",
                    )
                    network.socket.sendto(
                        pickle.dumps(message), network.get_ip_port(local_player.next)
                    )
                elif data.type == "end_shuffle":
                    break
                else:
                    print(
                        f"Player {local_player.ip} was expecting type shuffle or end_shuffle, received {data.type} from {data.origin}"
                    )

            else:
                # Passa a mensagem adiante se não for destinada ao jogador local
                network.socket.sendto(raw_data, network.get_ip_port(local_player.next))

        data = None


def create_shuffled_deck(cards_in_round: int, num_players: int) -> list:
    deck = list(range(1, 14)) * 4
    random.shuffle(deck)
    return deck[: num_players * cards_in_round]


def distribute_cards(dealer: Player, network: Network, cards_in_round: int):
    input("Press a key to start shuffling: ")
    deck = create_shuffled_deck(cards_in_round, len(network.players))

    for card_index, card in enumerate(deck):
        player = network.players[card_index // cards_in_round]
        if player.id == dealer.id:
            dealer.receive_card(card)  # Dealer directly receives the card
        else:
            # Serialize and send the card to the player
            message = pickle.dumps(
                Message(dealer.id, dealer.ip, player.ip, "shuffle", card)
            )
            network.socket.sendto(message, network.get_ip_port(dealer.next))

            while True:
                raw_data = network.socket.recv(4096)
                data = pickle.loads(raw_data)

                if data.dest == dealer.ip:
                    if data.type == "confirm_shuffle":
                        break
                    else:
                        print(
                            f"Player {dealer.ip} was expecting type confirm_shuffle, received {data.type} from {data.origin}"
                        )
                else:
                    # Passa a mensagem adiante se não for destinada ao jogador local
                    network.socket.sendto(raw_data, network.get_ip_port(dealer.next))

    # Send end_shuffle message
    for player in network.get_reversed_ordered_players():
        if player.id != dealer.id:
            end_message = pickle.dumps(
                Message(player.id, dealer.ip, player.ip, "end_shuffle", "", "")
            )
            network.socket.sendto(end_message, network.get_ip_port(dealer.next))
