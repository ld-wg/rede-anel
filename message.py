import time


class Message:
    """
    A class to represent messages sent between players in a networked card game.

    Attributes:
        owner (int): The ID of the player who owns this message.
        origin (str): The network address of the sender.
        dest (str): The network address of the recipient.
        type (str): The type of the message (e.g., 'shuffle', 'bid', 'play').
        play (any): The content of the message, typically which card is played or other relevant data.
        confirm (bool): A flag to confirm receipt or other binary conditions.
    """

    VALID_TYPES = {
        "shuffle",
        "bid",
        "play",
        "ack_play",
        "end_play",
        "confirm_shuffle",
        "end_shuffle",
        "end_bid",
        "update_hp",
        "round_won",
    }

    def __init__(self, owner, origin, dest, type, play, confirm):
        assert type in self.VALID_TYPES, f"Invalid message type: {type}"
        self.owner = owner  # The ID of the message sender
        self.origin = origin  # IP address of the sender
        self.dest = dest  # IP address of the recipient
        self.type = type  # Type of message ('shuffle', 'play', etc.)
        self.play = play  # Content of the message, e.g., card played
        self.confirm = confirm  # Boolean to confirm actions or receipt

    def __str__(self):
        return f"Message: {self.origin} to {self.dest} - T: {self.type}, P: {self.play}, C: {self.confirm}"
