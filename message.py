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

    VALID_TYPES = {"shuffle", "bid", "play", "confirm_shuffle", "end_shuffle"}

    def __init__(self, owner, origin, dest, m_type, play, confirm):
        assert m_type in self.VALID_TYPES, f"Invalid message type: {m_type}"
        self.owner = owner  # The ID of the message sender
        self.origin = origin  # IP address of the sender
        self.dest = dest  # IP address of the recipient
        self.type = m_type  # Type of message ('shuffle', 'play', etc.)
        self.play = play  # Content of the message, e.g., card played
        self.confirm = confirm  # Boolean to confirm actions or receipt

    def __str__(self):
        return (
            f"Message from {self.origin} to {self.dest} - Type: {self.type}, "
            f"Play: {self.play}, Confirmed: {self.confirm}, Timestamp: {self.timestamp}"
        )