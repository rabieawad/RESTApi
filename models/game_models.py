from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field


class PlayerModel(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)

    name: str


class LobbyModel(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    status: str = 'open'
    maxPlayers: int = 2
    players: List[PlayerModel] = []
    creation_time: datetime = Field(default_factory=datetime.now)

class GameModel(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    word: str = None
    max_attempts: int = 6
    status: str = 'open'
    winner: PlayerModel | None = None
    players: List[PlayerModel] = []
    word_status: str = ''
    guessed_chars: List = []