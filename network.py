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
                player_id=player_info["id"],
                ip=player_info["addr"],
                port=player_info["port"],
            )
            self.players.append(new_player)

    def _link_players(self):
        for i, player in enumerate(self.players):
            player.next = self.players[(i + 1) % len(self.players)]

    def _assign_initial_dealer(self):
        self.players[0].set_dealer()

    def find_dealer(self) -> Player:
        for player in self.players:
            if player.dealer:
                return player
        raise ValueError("Dealer not found")

    def pass_dealer(self):
        current_dealer = self.players[0]
        for player in self.players:
            if player.dealer:
                current_dealer = player

        current_dealer.next.set_dealer()
        current_dealer.unset_dealer()

    def get_player_by_id(self, id) -> Player:
        for player in self.players:
            if player.id == id:
                return player
        raise ValueError("Player not found")

    def get_player_by_ip(self, ip) -> Player:
        for player in self.players:
            if player.ip == ip:
                return player
        raise ValueError("Player not found")

    """Returns the next player in the ring network."""

    def get_next_player(self, player) -> Player:
        return player.next

    """Returns the IP and port of the next player in the ring network."""

    def get_ip_port(self, player: Player) -> Tuple[any, any]:
        return player.ip, player.port

    """"Removes players with hp == 0."""

    def remove_dead_players(self):
        for player in self.players:
            if player.hp == 0:
                self.remove_player(player)

    """Removes a player from the network and re-links the remaining players."""

    def remove_player(self, player_to_remove):
        self.players = [player for player in self.players if player != player_to_remove]
        self._link_players()

    """Reset players status for new round to begin"""

    def reset_players_for_new_round(self):
        for player in self.players:
            player.reset_for_new_round()

    """Binds the network socket to the specified IP and returns the corresponding player."""

    def get_chair(self, ip) -> Player:
        for player in self.players:
            if player.ip == ip:
                self.socket.bind((player.ip, player.port))
                return player
        raise ValueError("Player not found")

    def get_players_starting_with(self, starting_player: Player) -> list[Player]:
        ordered_players = [starting_player]
        current_player = starting_player.next

        while current_player != starting_player:
            ordered_players.append(current_player)
            current_player = current_player.next

        return ordered_players

    def __repr__(self):
        return f"Network(players={self.players})"
