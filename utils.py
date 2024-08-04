import random
import pickle
from message import Message
from player import Player
from network import Network


def get_cards(network: Network, cards_in_round: int):
    dealer = network.find_dealer()

    starting_player = dealer

    for _ in range(cards_in_round):
        dealer.reset_plays()
        for player in network.get_players_starting_with(starting_player):
            if player.id == dealer.id:
                dealer.plays.append((player.play_card(), player.id))
            else:
                # Envia mensagem pedindo a carta do jogador
                play_message = pickle.dumps(
                    Message(dealer.id, dealer.ip, player.ip, "play", "", "")
                )
                network.socket.sendto(play_message, network.get_ip_port(dealer.next))

                # Espera a resposta do lance do jogador
                while True:
                    raw_data = network.socket.recv(4096)
                    data: Message = pickle.loads(raw_data)

                    if data.dest == dealer.ip:
                        if data.type == "play" and data.confirm == "true":
                            dealer.plays.append((int(data.play), data.owner))
                            print(f"Play received from {data.origin}: {data.play}")
                            break
                        else:
                            print(
                                f"Player {dealer.ip} was expecting type play and confirm true, received {data.type} from {data.origin}"
                            )
                    else:
                        network.socket.sendto(
                            raw_data, network.get_ip_port(dealer.next)
                        )

                    data = None
        result = get_winner(dealer)

        if result != "draw":
            winner = network.get_player_by_id(result)
            winner.win_round()
            print(f"Player {winner.ip} won this play!")
            starting_player = winner
        else:
            print("Draw")

    # Após receber todos as jogadas da rodada, envia a mensagem de finalização de rodada
    for player in network.players:
        if player.id != dealer.id:
            end_bid_message = pickle.dumps(
                Message(dealer.id, dealer.ip, player.ip, "end_play", "", "")
            )
            network.socket.sendto(end_bid_message, network.get_ip_port(dealer.next))
            while True:
                raw_data = network.socket.recv(4096)
                data: Message = pickle.loads(raw_data)
                print(data)

                if data.dest == dealer.ip:
                    if data.type == "end_play":
                        if data.confirm == "true":
                            break
                        else:
                            print(f"confirm_shuffle from {data.dest} was not confirmed")
                    else:
                        print(
                            f"Player {dealer.ip} was expecting type end_play, received {data.type} from {data.origin}"
                        )
                else:
                    # Passa a mensagem adiante se não for destinada ao jogador local
                    network.socket.sendto(raw_data, network.get_ip_port(dealer.next))


def wait_get_cards(network: Network, local_player: Player):
    while True:
        raw_data = network.socket.recv(4096)
        data: Message = pickle.loads(raw_data)

        if data:
            if data.dest == local_player.ip:
                if data.type == "play":
                    # Jogador recebe o lance e envia sua resposta
                    play = local_player.play_card()

                    response_message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "play",
                        play,
                        "true",
                    )
                    network.socket.sendto(
                        pickle.dumps(response_message),
                        network.get_ip_port(local_player.next),
                    )

                elif data.type == "end_play":
                    response_message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "end_play",
                        "",
                        "true",
                    )
                    network.socket.sendto(
                        pickle.dumps(response_message),
                        network.get_ip_port(local_player.next),
                    )
                    break  # Sai do loop após confirmar o fim do lance
                else:
                    print(
                        f"Player {local_player.ip} was expecting type play or end_play, received {data.type} from {data.origin}"
                    )

            else:
                # Passa a mensagem adiante se não for destinada ao jogador local
                network.socket.sendto(raw_data, network.get_ip_port(local_player.next))

        data = None


def get_winner(dealer: Player):
    highest_card = 0
    winners = []

    for card_value, player_id in dealer.plays:
        if card_value > highest_card:
            highest_card = card_value
            winners = [player_id]  # Start a new list with the current player
        elif card_value == highest_card:
            winners.append(player_id)  # Add to the list of winners if there is a tie

    # Determine if there's a draw or a single winner
    if len(winners) > 1:
        return "draw"
    else:
        return winners[0]  # Return the ID of the winner


def get_bid(cards_in_round: int) -> int:
    bid = 0
    while bid == 0:
        bid_input = input(f"Insira seu palpite, de 1 a {cards_in_round}: ")
        try:
            bid = int(bid_input)  # Attempt to convert input to an integer
            if bid < 1 or bid > cards_in_round:
                print(f"Palpite invalido, precisa ser de 1 a {cards_in_round}")
                bid = 0  # Reset bid to keep the loop going
        except ValueError:
            print("Por favor, insira um número válido.")
            bid = 0  # Ensure bid is reset if input is not a valid integer
    return bid


def send_bids(network: Network, cards_in_round: int):
    input("Press a key to start collecting bids: ")
    dealer = network.find_dealer()
    # Para cada jogador, envia a mensagem de "bid" e aguarda confirmacao
    for player in network.players:
        if player.id == dealer.id:
            dealer.set_bid(
                get_bid(cards_in_round)
            )  # Set the dealer's bid once a valid input is received

        else:
            # Cria a mensagem de lance inicial
            bid_message = pickle.dumps(
                Message(dealer.id, dealer.ip, player.ip, "bid", "", "")
            )
            network.socket.sendto(bid_message, network.get_ip_port(dealer.next))

            # Espera a resposta do lance do jogador
            while True:
                raw_data = network.socket.recv(4096)
                data: Message = pickle.loads(raw_data)

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
    for player in network.players:
        if player.id != dealer.id:
            end_bid_message = pickle.dumps(
                Message(dealer.id, dealer.ip, player.ip, "end_bid", "", "")
            )
            network.socket.sendto(end_bid_message, network.get_ip_port(dealer.next))
            while True:
                raw_data = network.socket.recv(4096)
                data: Message = pickle.loads(raw_data)
                print(data)

                if data.dest == dealer.ip:
                    if data.type == "end_bid":
                        if data.confirm == "true":
                            break
                        else:
                            print(f"confirm_shuffle from {data.dest} was not confirmed")
                    else:
                        print(
                            f"Player {dealer.ip} was expecting type end_shuffle, received {data.type} from {data.origin}"
                        )
                else:
                    # Passa a mensagem adiante se não for destinada ao jogador local
                    network.socket.sendto(raw_data, network.get_ip_port(dealer.next))


def wait_and_respond_to_bids(
    local_player: Player, network: Network, cards_in_round: int
):
    while True:
        raw_data = network.socket.recv(4096)
        data: Message = pickle.loads(raw_data)

        if data:
            if data.dest == local_player.ip:
                if data.type == "bid":
                    # Jogador recebe o lance e envia sua resposta
                    bid = get_bid(cards_in_round)

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
                    response_message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "end_bid",
                        "",
                        "true",
                    )
                    network.socket.sendto(
                        pickle.dumps(response_message),
                        network.get_ip_port(local_player.next),
                    )
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
        data: Message = pickle.loads(raw_data)

        if data:
            if data.dest == local_player.ip:
                if data.type == "shuffle":
                    local_player.receive_card(data.play)
                    message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "shuffle",
                        "",
                        "true",
                    )
                    network.socket.sendto(
                        pickle.dumps(message), network.get_ip_port(local_player.next)
                    )
                elif data.type == "end_shuffle":
                    message = Message(
                        local_player.id,
                        local_player.ip,
                        data.origin,
                        "end_shuffle",
                        "",
                        "true",
                    )
                    network.socket.sendto(
                        pickle.dumps(message), network.get_ip_port(local_player.next)
                    )
                    print("HAHAHAH")
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
                Message(dealer.id, dealer.ip, player.ip, "shuffle", card, "")
            )
            network.socket.sendto(message, network.get_ip_port(dealer.next))

            while True:
                raw_data = network.socket.recv(4096)
                data: Message = pickle.loads(raw_data)
                print(data)

                if data.dest == dealer.ip:
                    if data.type == "shuffle":
                        if data.confirm == "true":
                            break
                        else:
                            print(f"confirm_shuffle from {data.dest} was not confirmed")
                    else:
                        print(
                            f"Player {dealer.ip} was expecting type shuffle, received {data.type} from {data.origin}"
                        )
                else:
                    # Passa a mensagem adiante se não for destinada ao jogador local
                    network.socket.sendto(raw_data, network.get_ip_port(dealer.next))

    # Send end_shuffle message
    for player in network.players:
        if player.id != dealer.id:
            end_message = pickle.dumps(
                Message(dealer.id, dealer.ip, player.ip, "end_shuffle", "", "")
            )
            network.socket.sendto(end_message, network.get_ip_port(dealer.next))
            while True:
                raw_data = network.socket.recv(4096)
                data: Message = pickle.loads(raw_data)
                print(data)

                if data.dest == dealer.ip:
                    if data.type == "end_shuffle":
                        if data.confirm == "true":
                            break
                        else:
                            print(f"confirm_shuffle from {data.dest} was not confirmed")
                    else:
                        print(
                            f"Player {dealer.ip} was expecting type end_shuffle, received {data.type} from {data.origin}"
                        )
                else:
                    # Passa a mensagem adiante se não for destinada ao jogador local
                    network.socket.sendto(raw_data, network.get_ip_port(dealer.next))
