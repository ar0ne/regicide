"""Regicide game engine"""
from dataclasses import asdict
from typing import List

from core.games.base import AbstractGame, GameData, GameDataTurn, Id
from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Game
from core.games.regicide.internal import RegicideGameDataSerializer, RegicideGameLoader
from core.games.regicide.models import Card
from core.resources.models import GameTurn


class GameEngine(AbstractGame):
    """Regicide game engine"""

    def __init__(self, room_id: Id) -> None:
        """Init adapter"""
        self.room_id = room_id
        self.data_serializer = RegicideGameDataSerializer
        self.loader = RegicideGameLoader

    async def setup(self, players: List[Id]) -> None:
        """Setup new game"""
        game = Game.start_new_game(players)
        await self._save_game_state(game)

    async def update(self, player_id: Id, turn: GameDataTurn) -> None:
        """Update game state"""
        # transform from flat cards to Card objects
        data = list(map(lambda c: Card(c[0], c[1]), turn["cards"]))
        last_game_data = await self._get_latest_game_state()
        game = self.loader.load(last_game_data)
        # FIXME: move it all to validation method
        player = game.first_player
        if not player:
            raise Exception  # FIXME
        if player.id != player_id:
            raise Exception  # FIXME
        if game.is_playing_cards_state:
            game.play_cards(player, data)
        elif game.is_discarding_cards_state:
            game.discard_cards(player, data)
        else:
            # game ended?
            raise Exception  # FIXME
        # save changes
        await self._save_game_state(game)

    async def poll(self, player_id: Id | None = None) -> GameData | None:
        """Poll the last turn data"""
        last_turn_state = await self._get_latest_game_state()
        if not last_turn_state:
            return None
        game = self.loader.load(last_turn_state)
        return asdict(self.data_serializer.serialize(game, player_id))

    async def is_valid_turn(self, player_id: Id, turn: GameDataTurn) -> bool:
        """True if it's valid game turn"""
        # FIXME
        return True

    async def _get_latest_game_state(self) -> GameStateDto | None:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            return None
        return GameStateDto(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        game_state = self.loader.upload(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=game_state)
