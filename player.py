START_LIFE = 12  # Initialize with 12 lives


class Player:
    def __init__(self, player_id, ip, port, dealer):
        self.id = player_id
        self.ip = ip
        self.port = port
        self.dealer = dealer
        self.lives = START_LIFE
        self.cards = []
        self.round_wins = 0
        self.guess = 0
        self.stick = False
        self.round_starter = dealer
        self.consecutive_passes = 0
        self.next = None  # Link to the next player for the ring network

    def get_local(self):
        return {"ip": self.ip, "port": self.port}

    def get_stick(self):
        self.stick = True

    def drop_stick(self):
        self.stick = False

    def get_card(self, card):
        self.cards.append(int(card))

    def play_card(self, card):
        # TODO: Implement the logic for playing a card
        if self.cards:
            return self.card.pop(int(card))
        return None

    def win_round(self):
        self.round_wins += 1

    def get_roud_wins(self):
        return self.round_wins

    def __repr__(self):
        return (
            f"Player(id={self.id}, ip={self.ip}, port={self.port}, lives={self.lives})"
        )
