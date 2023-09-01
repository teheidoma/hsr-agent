import enum


class AgentStatus(enum.Enum):
    IDLE = 1,
    GAME_RUNNING = 2,
    TOKEN_ERROR = 3
