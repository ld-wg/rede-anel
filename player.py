import os

START_HP = 12  # Initialize with 12 hp


class Player:
    def __init__(self, player_id: str, ip: str, port: str):
        self.id = player_id
        self.ip = ip
        self.port = port
        self.dealer = False
        self.hp = START_HP
        self.cards = []
        self.round_wins = 0
        self.bid = 0
        self.next: Player = None  # Link to the next player for the ring network
        self.plays: list[tuple[int, str]] = []

    def reset_for_new_round(self):
        self.cards = []
        self.plays = []
        self.bid = 0
        self.round_wins = 0

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
                    print(f"You played {card_input}")
                    return card_input
                else:
                    print("Sorry, you don't have this card. Please try another.")
            except ValueError:
                print("Please enter a valid number.")

    def update_hp(self):
        # Calculate the potential new HP
        potential_hp = self.hp - abs(self.bid - self.round_wins)
        # Check if the new HP is negative
        if potential_hp < 0:
            self.hp = 0
        else:
            self.hp = potential_hp

    def set_hp(self, hp):
        self.hp = int(hp)

    def set_bid(self, bid):
        self.bid = int(bid)

    def set_dealer(self):
        self.dealer = True

    def unset_dealer(self):
        self.dealer = False

    def get_local(self):
        return {"ip": self.ip, "port": self.port}

    def win_round(self):
        self.round_wins += 1

    def get_roud_wins(self) -> int:
        return self.round_wins

    def reset_plays(self):
        self.plays = []

    def __repr__(self):
        return f"Player(id={self.id}, ip={self.ip}, port={self.port}, hp={self.hp})"
