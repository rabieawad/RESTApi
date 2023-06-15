from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from models.game_models import GameModel, LobbyModel, PlayerModel
from utils.db_helpers import get_game_by_id, get_lobby_by_id, get_player_by_id
from utils.game_helpers import find_all_occurrences, replace_char_at_indices
from utils.hangman_drawer import show_hangman
from utils.io_helpers import get_random_word

# Main Fastapi instance
app = FastAPI()

# For simplicity, we use in-memory data structures instead of a database
lobbies = []
players = []
games = []
game_sessions = {}

# Maintain a dictionary of active WebSocket connections
ws_connections = {}


@app.get("/lobbies")
async def get_lobbies():
    """
    Retrieves a list of lobbies.

    Returns:
        List[LobbyModel]: List of lobbies.

    Example:
        [
            {
                "id": 1,
                "name": "Lobby 1",
                "players": []
            },
            {
                "id": 2,
                "name": "Lobby 2",
                "players": ["Alice", "Bob"]
            }
        ]
    """
    return lobbies


@app.get('/players')
async def get_players():
    """
    Retrieves a list of players.

    Returns:
        List[PlayerModel]: List of players.

    Example:
        [
            {
                "id": 1,
                "name": "Alice"
            },
            {
                "id": 2,
                "name": "Bob"
            }
        ]
    """
    return players


@app.get("/games")
async def get_games():
    """
    Retrieves a list of games.

    Returns:
        List[GameModel]: List of games.

    Example:
        [
            {
                "id": 1,
                "name": "Game 1",
                "players": ["Alice", "Bob"],
                "status": "In Progress"
            },
            {
                "id": 2,
                "name": "Game 2",
                "players": ["Charlie"],
                "status": "Waiting"
            }
        ]
    """
    return games


@app.get("/ws_conns")
async def get_ws_connections():
    """
    Retrieves the WebSocket connection counts for each identifier.

    Returns:
        dict: A dictionary containing the WebSocket connection counts for each identifier.

    Example:
        {
            "player1": 2,
            "player2": 3,
            "player3": 1
        }
    """

    # NOTE: This function is for debugging purposes and should not be used in production.
    # It returns the current count of WebSocket connections for each identifier.

    connection_counts = {k: len(v) for k, v in ws_connections.items()}
    return connection_counts


@app.get("/status/{game_id}")
async def get_status_player(game_id: str):
    """
    Retrieves the status of a player and the word status for a specific game.

    Args:
        game_id (str): The ID of the game to retrieve the status for.

    Returns:
        dict: A dictionary containing the player status and the word status.

    Example:
        {
            "player_status": "player1",
            "word_status": "a-p-e"
        }
    """
    game: GameModel = get_game_by_id(games, game_id)
    return {
        "player_status": game.players[0].id,
        "word_status": game.word_status
    }


@app.post('/create_lobby')
async def create_lobby(lobby: LobbyModel):
    """
    Creates a new lobby.

    Args:
        lobby (LobbyModel): The lobby details.

    Returns:
        LobbyModel: The created lobby.

    Example:
        {
            "id": 1 - Auto Generated,
            "name": "Lobby 1",
            "players": []
        }
    """
    lobbies.append(lobby)
    return lobby


@app.post('/create_player')
async def create_player(player: PlayerModel):
    """
    Creates a new player.

    Args:
        player (PlayerModel): The player details.

    Returns:
        PlayerModel: The created player.

    Example:
        {
            "id": 1 - Auto Generated,
            "name": "Alice"
        }
    """
    players.append(player)
    return player


@app.post('/lobby/{lobby_id}/join/{player_id}')
async def join_player_lobby(lobby_id: str, player_id: str):
    """
    Adds a player to a lobby.

    Args:
        lobby_id (str): The ID of the lobby to join.
        player_id (str): The ID of the player to add.

    Returns:
        LobbyModel: The updated lobby after adding the player.

    Raises:
        HTTPException(403): If the lobby is closed and cannot accept more players.
        HTTPException(404): If the lobby or player is not found.

    Example:
        {
            "id": "lobby1",
            "name": "Lobby 1",
            "players": ["player1", "player2"],
            "status": "closed"
        }
    """
    player = get_player_by_id(players, player_id)
    lobby = get_lobby_by_id(lobbies, lobby_id)

    if lobby is None or player is None:
        raise HTTPException(
            status_code=404, detail="Lobby or player not found.")

    if lobby.status == 'closed':
        raise HTTPException(status_code=403, detail="Lobby is closed.")

    lobby.players.append(player)

    if len(lobby.players) == lobby.maxPlayers:
        lobby.status = 'closed'

    return lobby


@app.websocket("/multicast/{lobby_id}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str):
    """
    WebSocket endpoint for multicast messages in a lobby.

    Args:
        websocket (WebSocket): The WebSocket connection object.
        lobby_id (str): The ID of the lobby.

    Raises:
        WebSocketDisconnect: If the WebSocket connection is disconnected.

    Notes:
        - This endpoint expects messages from connected clients in the lobby.
        - It multicast the received message to Specific connected clients in the lobby.
        - If the lobby is full, it broadcasts a "lobby is full" status to the clients.
        - If the WebSocket connection is disconnected, it removes the connection from the lobby.
        - Handles other exceptions that may occur during WebSocket communication.

    Example:
        Lobby ID: "lobby1"
    NOTE: In Production, remove print statements. For DEBUGGING
    """
    # Broadcast that a new player has joined the lobby
    print("Lobby ID:", lobby_id)
    await websocket.accept()

    if lobby_id not in ws_connections:
        ws_connections[lobby_id] = []

    ws_connections[lobby_id].append(websocket)
    print(ws_connections)

    try:
        while True:
            lobby = get_lobby_by_id(lobbies, lobby_id)
            data = await websocket.receive_text()
            user = get_player_by_id(players, data)
            sock_data = f"Username: {user.name} with ID: {user.id} joined the lobby"

            game = None

            # Broadcast the received message to all connected clients in the lobby
            for connection in ws_connections[lobby_id]:
                if lobby.maxPlayers == len(lobby.players):
                    # Broadcast status to clients that the lobby is full
                    if game is None:
                        random_word = get_random_word()
                        game = GameModel(
                            word=random_word,
                            max_attempts=6,
                            players=lobby.players,
                            word_status="-" * len(random_word)
                        )
                        games.append(game)
                    payload = {
                        "status": "done",
                        "game_id": game.id
                    }
                    await connection.send_json(payload)
                else:
                    if connection != websocket:
                        payload = {
                            "message": sock_data
                        }
                        await connection.send_json(payload)

    except WebSocketDisconnect:
        # Handle disconnection gracefully
        ws_connections[lobby_id].remove(websocket)

    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {str(e)}")
        ws_connections[lobby_id].remove(websocket)


@app.post("/guess/{game_id}/{user_id}/{char}")
async def make_guess(game_id: str, user_id: str, char: str):
    """
    Make a guess for the given game, user, and character.

    Args:
        game_id (str): The ID of the game.
        user_id (str): The ID of the user making the guess.
        char (str): The character being guessed.

    Raises:
        HTTPException: If the guess is invalid or if it's not the player's turn to guess.

    Returns:
        dict: The response containing the game status and relevant details.

    Notes:
        - This endpoint allows a user to make a guess for the given game by providing the game ID, user ID, and character.
        - The guess is validated, and the game status and word status are updated accordingly.
        - If the guess is correct and the word is fully guessed, the game is finished, and the user is declared the winner.
        - If the guess is incorrect, the user loses a life, and the hangman status is updated.
        - The game state is maintained in the game_sessions dictionary.

    """
    game: GameModel = get_game_by_id(games, game_id)
    player = get_player_by_id(players, user_id)

    if len(char) != 1:
        raise HTTPException(
            status_code=400, detail="Invalid parameter: char length should be 1"
        )

    # Check if it's the player's turn
    if player.id != game.players[0].id:
        raise HTTPException(
            status_code=400, detail="It's not your turn to guess."
        )

    if game.status != "open":
        winner = await get_player_by_id(players, game.winner)
        raise HTTPException(
            status_code=400,
            detail=f"Game has already finished. WinnerId: {winner.id}, Winner Name: {winner.name}",
        )

    game.players = game.players[1:] + [game.players[0]]

    # Initialize Game Session
    if not game_sessions.get(game_id):
        print("Initialize Game Session")
        game_sessions[game_id] = {
            user_id: {
                "lives": game.max_attempts
            }
        }

    # Initialize UserID in game Sessions
    if not game_sessions[game_id].get(user_id):
        game_sessions[game_id][user_id] = {
            "lives": game.max_attempts
        }

    if game_sessions[game_id][user_id]["lives"] == 0:
        games.remove(game)
        game.players.remove(player)
        print(game)
        games.append(game)
        raise HTTPException(
            status_code=400, detail="You have run out of lives. Game over."
        )

    if char in game.word and char not in game.guessed_chars:
        game.guessed_chars.append(char)
        indices = find_all_occurrences(game.word, char)
        game.word_status = replace_char_at_indices(
            game.word_status, indices, char
        )

        if game.word_status == game.word:
            game.status = "finished"
            game.winner = user_id
            return {
                "detail": "Congratulations! You guessed the word correctly. You are the winner.",
                "word_status": game.word_status,
                "game": game,
            }

        return {
            "detail": f"You guessed the character: Word status {game.word_status}",
            "lives": game_sessions[game_id][user_id]["lives"],
        }

    else:
        game_sessions[game_id][user_id]["lives"] -= 1
        if game_sessions[game_id][user_id]["lives"] == 0:
            # games.remove(game)
            game.players.remove(player)
            

    return {
        "detail": f"Invalid character: Word status {game.word_status}, lives: {game_sessions[game_id][user_id]['lives']}",
        "hangman": show_hangman(5 - game_sessions[game_id][user_id]["lives"]),
        "lives": game_sessions[game_id][user_id]["lives"],
    }
