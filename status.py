import enum
import json


class ErrorCode(str, enum.Enum):
    TOKEN_GAME_MISSING_1 = "TOKEN_GAME_MISSING_1",
    TOKEN_GAME_MISSING_2 = "TOKEN_GAME_MISSING_2",
    TOKEN_GAME_MISSING_3 = "TOKEN_GAME_MISSING_3",
    TOKEN_GAME_MISSING_4 = "TOKEN_GAME_MISSING_4",
    TOKEN_GAME_UPDATE = "TOKEN_GAME_UPDATE"


class AgentStatus(str, enum.Enum):
    IDLE = 'IDLE',
    IMPORT = 'IMPORT',
    GAME_RUNNING = 'GAME_RUNNING',
    ERROR = 'ERROR'


class Status:
    def __init__(self):
        self._status = None
        self._error = None

    def status(self, status: AgentStatus):
        self._status = status
        self._error = None

    def error(self, code: ErrorCode, message: str = None):
        self._status = AgentStatus.ERROR
        self._error = StatusError(code, message)

    def to_response(self):
        response = {}
        if self._status:
            response['status'] = self._status
        if self._error:
            response['error'] = self._error.to_dict()
        return json.dumps(response)

    def clear(self):
        self.status(AgentStatus.IDLE)
        pass


class StatusError:
    def __init__(self, code: ErrorCode, message: str = None):
        self.code = code
        self.message = message

    def to_dict(self):
        dict = {}
        if self.code:
            dict['code'] = self.code
        if self.message:
            dict['message'] = self.message
        return dict
