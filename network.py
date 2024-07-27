import socket
import json
from player import Player


class Network:
    def __init__(self, config_file_path="config.json"):
        self.players = []
        self.socket = self._create_socket()
        self._load_config(config_file_path)
        self._init_players()
        self._link_players()

    def _create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _load_config(self, config_file_path):
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            self.num_players = config["num_players"]
            self.config_players = config["players"]

    def _init_players(self):
        for player_info in self.config_players:
            new_player = Player(
                player_info["id"],
                player_info["addr"],
                player_info["port"],
                player_info["dealer"],
            )
            if new_player.dealer:
                new_player.get_stick()
            self.players.append(new_player)

    def _link_players(self):
        for i, player in enumerate(self.players):
            player.next = self.players[(i + 1) % self.num_players]
