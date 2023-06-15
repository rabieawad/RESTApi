from fastapi import HTTPException

from models.game_models import GameModel, LobbyModel, PlayerModel


def get_player_by_id(db: list, player_id: str) -> PlayerModel:

    """Gets a player by their ID.

    Args:
    db: A list of PlayerModel objects.
    player_id: The ID of the player to get.

    Returns:
    The PlayerModel object with the given ID.

    Raises:
    HTTPException: If the player is not found.
    """

    for player in db:
        if player.id == player_id:
            return player

    raise HTTPException(
        status_code=404, detail=f"Player Not Found with id: {player_id}")


def get_lobby_by_id(db: list, lobby_id: str) -> LobbyModel:

    """Gets a lobby by its ID.

    Args:
    db: A list of LobbyModel objects.
    lobby_id: The ID of the lobby to get.

    Returns:
    The LobbyModel object with the given ID.

    Raises:
    HTTPException: If the lobby is not found.
    """

    for lobby in db:
        if lobby.id == lobby_id:
            return lobby

    raise HTTPException(
        status_code=404, detail=f"Lobby Not Found with id: {lobby_id}")


def get_game_by_id(db: list, game_id: str) -> GameModel:

    """Gets a game by its ID.

    Args:
    db: A list of GameModel objects.
    game_id: The ID of the game to get.

    Returns:
    The GameModel object with the given ID.

    Raises:
    HTTPException: If the game is not found.
    """

    for game in db:
        if game.id == game_id:
            return game

    raise HTTPException(
        status_code=404, detail=f"Game Not Found with id: {game_id}")