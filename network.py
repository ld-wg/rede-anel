import socket
import json
from player import Player
from typing import Tuple


class Network:
    def __init__(self, config_file_path="config.json"):
        self.players: list[Player] = []
        self.socket = self._create_socket()
        self._load_config(config_file_path)
        self._init_players()
        self._link_players()
        self._assign_initial_dealer()

    def _create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _load_config(self, config_file_path: str):
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            self.config_players = config["players"]

        config_file.close()

    def _init_players(self):
        for player_info in self.config_players:
            new_player = Player(
                player_info["id"],
                player_info["addr"],
                player_info["port"],
            )
            self.players.append(new_player)

    def _link_players(self):
        for i, player in enumerate(self.players):
            player.next = self.players[(i + 1) % len(self.players)]

    def _assign_initial_dealer(self):
        self.players[0].set_dealer()
        self.players[0].get_stick()

    def find_dealer(self) -> Player:
        for player in self.players:
            if player.dealer:
                return player
        raise ValueError("Dealer not found")

    def pass_dealer(self):
        current_dealer = self.find_dealer()
        current_dealer.next.set_dealer()
        current_dealer.unset_dealer()

    def get_player_by_id(self, id) -> Player:
        for player in self.players:
            if player.id == id:
                return player
        raise ValueError("Player not found")

    """Returns the next player in the ring network."""

    def get_next_player(self, player) -> Player:
        return player.next

    """Returns the IP and port of the next player in the ring network."""

    def get_ip_port(self, player: Player) -> Tuple[any, any]:
        return player.ip, player.port

    """Removes a player from the network and re-links the remaining players."""

    def remove_player(self, player_id):
        self.players = [player for player in self.players if player.id != player_id]
        self._link_players()

    """Binds the network socket to the specified IP and returns the corresponding player."""

    def get_chair(self, ip) -> Player:
        for player in self.players:
            if player.ip == ip:
                self.socket.bind((player.ip, player.port))
                return player
        raise ValueError("Player not found")

    """Retorna uma lista dos jogadores ordenados de player.anterior ate player.proximo."""
    # Funcao utilizada para finalizar rotinas, um jogador envia mensagem para os outros pararem de escutar
    # Se faz necessario "desligar" os jogadores na ordem correta, ou a integridade da rede pode ser prejudicada

    def get_reversed_ordered_players(self, starting_player: Player) -> list[Player]:
        ordered_players = []
        current_player = starting_player.next  # Começa com o jogador seguinte

        # Continua até que o loop retorne ao jogador de partida
        while current_player != starting_player:
            ordered_players.append(current_player)
            current_player = (
                current_player.next
            )  # Move para o próximo jogador na sequência

        # Reverte a lista para começar pelo jogador anterior ao de entrada
        return ordered_players.reverse()

    def __repr__(self):
        return f"Network(players={self.players})"
