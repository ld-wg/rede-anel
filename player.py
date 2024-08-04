from typing import Tuple


START_LIFE = 12  # Initialize with 12 lives


class Player:
    def __init__(self, player_id: str, ip: str, port: str):
        self.id = player_id
        self.ip = ip
        self.port = port
        self.dealer = False
        self.lives = START_LIFE
        self.cards = []
        self.round_wins = 0
        self.bid = 0
        self.stick = False
        self.turn = False
        self.next: Player = None  # Link to the next player for the ring network
        self.plays: list[tuple[int, str]] = []

    def receive_card(self, card):
        print(f"Player {self.ip} received card {card}")
        self.cards.append(int(card))
        self.cards.sort()

    def play_card(self) -> int:
        while True:
            try:
                card_input = int(input(f"Choose a card from your hand: {self.cards} "))
                if card_input in self.cards:
                    self.cards.remove(card_input)
                    return card_input
                else:
                    print("Sorry, you don't have this card. Please try another.")
            except ValueError:
                print("Please enter a valid number.")

    def set_bid(self, bid):
        self.bid = int(bid)

    def set_dealer(self):
        self.dealer = True

    def unset_dealer(self):
        self.dealer = False

    def get_local(self):
        return {"ip": self.ip, "port": self.port}

    def get_stick(self):
        self.stick = True

    def drop_stick(self):
        self.stick = False

    def win_round(self):
        self.round_wins += 1

    def get_roud_wins(self) -> int:
        return self.round_wins

    def reset_plays(self):
        self.plays = []

    def __repr__(self):
        return (
            f"Player(id={self.id}, ip={self.ip}, port={self.port}, lives={self.lives})"
        )
