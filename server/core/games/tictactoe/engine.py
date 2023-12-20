"""Tic Tac Toe game engine"""
from dataclasses import asdict
from typing import List, Self, Tuple, Type

from core.constants import GameRoomStatus
from core.games.base import AbstractGame, BaseGameEngine, GameData, GameDataTurn
from core.games.exceptions import GameDataNotFound
from core.games.tictactoe.dto import GameStateDto
from core.games.tictactoe.game import Game
from core.games.tictactoe.models import Status
from core.games.tictactoe.serializers import TicTacToeGameStateDataSerializer
from core.games.transform import GameStateDataSerializer
from core.resources.models import GameTurn


class TicTacToeGameEngine(BaseGameEngine):
    """TicTacToe game engine"""

    GAME_CLS = Game
    STATUSES_IN_PROGRESS = (Status.CREATED, Status.IN_PROGRESS)

    def __init__(self, room_id: str, state_serializer: GameStateDataSerializer) -> None:
        """init game engine"""
        self.room_id = room_id
        self.state_serializer = state_serializer

    async def update(self, player_id: str, turn: GameDataTurn) -> Tuple[GameData, str]:
        """Update game state"""
        game_data = GameStateDto(**await self.get_latest_game_data())
        game = self.state_serializer.load(game_data)
        # update state
        game = self.GAME_CLS.make_turn(game, player_id, turn)
        # save changes
        await self.save_game_state(game)
        # serialize updated game state
        game_turn = self.state_serializer.dump(game)
        return asdict(game_turn), game.status

    async def poll(self, player_id: str | None = None) -> GameData:
        """Poll the last game state"""
        last_state = GameStateDto(await self.get_latest_game_data())
        player_id = str(player_id) if player_id else None
        # we don't need to hide anything from other users, just serialize state
        return dict(player_id=player_id, **asdict(last_state))


def create_engine(room_id: str) -> AbstractGame:
    """Game engine builder"""
    return TicTacToeGameEngine(
        room_id=room_id,
        state_serializer=TicTacToeGameStateDataSerializer,
    )
