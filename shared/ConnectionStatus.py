import enum

class ConnectionStatus(enum.Enum):
    CONNECTING = 1
    CONNECTED = 2
    FAILED = 3