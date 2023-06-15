import asyncio
import json
import sys
from time import sleep

import requests
import websockets
from rich import print

API_URL = "http://localhost:8000"  # Replace with your FastAPI server URL

user_name = ""
user_id = ""
server_id = ""
game_id = ""

# Function to create a new player


def create_player():
    """
    Create a new player by prompting for the name and sending a POST request to the server.

    The created player's name and ID are stored in the global variables 'user_name' and 'user_id'.

    Raises:
        - None

    Returns:
        - None
    """
    global user_name, user_id
    name = input("Enter your name: ")
    player = {"name": name}
    response = requests.post(f"{API_URL}/create_player", json=player)
    if response.status_code == 200:
        player_data = response.json()
        user_name = player_data["name"]
        user_id = player_data["id"]
        print("[bold green]Player created successfully![/bold green]")
        print(f"[bold]Player ID:[/bold] {user_id}")
    else:
        print("[bold red]Failed to create player.[/bold red]")


def create_or_join_lobby():
    """
    Prompt the user to create a new lobby or join an existing lobby based on their choice.

    The user's choice is obtained from the input. If the choice is 'C', the function calls the
    'create_new_lobby' function. If the choice is 'J', the function calls the 'join_existing_lobby' function.
    If the choice is neither 'C' nor 'J', an error message is displayed.

    Raises:
        - None

    Returns:
        - None
    """
    global server_id
    choice = input("Create new lobby (C) or join existing lobby (J)? ")
    if choice.upper() == "C":
        create_new_lobby()
    elif choice.upper() == "J":
        join_existing_lobby()
    else:
        print("[bold red]Invalid choice. Please try again.[/bold red]")



# Function to create a new lobby
def create_new_lobby():
    """
    Create a new lobby by sending a request to the API with the specified maximum number of players.

    The function prompts the user to enter the maximum number of players for the lobby. It sends a POST
    request to the API URL with the provided maximum number of players in the request payload. If the
    response status code is 200, indicating a successful creation of the lobby, the function retrieves
    the lobby data from the response and sets the 'server_id' variable to the lobby ID. It then displays
    a success message along with the lobby ID and calls the 'join_existing_lobby' function to join the
    newly created lobby. If the response status code is not 200, an error message is displayed.

    Raises:
        - None

    Returns:
        - None
    """
    global server_id
    max_players = int(input("Enter the maximum number of players: "))
    lobby = {"maxPlayers": max_players}
    response = requests.post(f"{API_URL}/create_lobby", json=lobby)
    if response.status_code == 200:
        lobby_data = response.json()
        server_id = lobby_data["id"]
        print("[bold green]Lobby created successfully![/bold green]")
        print(f"[bold]Lobby ID:[/bold] {server_id}")
        join_existing_lobby(lobby_id=server_id)
    else:
        print("[bold red]Failed to create lobby.[/bold red]")



# Function to join an existing lobby
def join_existing_lobby(lobby_id=None):
    """
    Join an existing lobby by sending a request to the API with the provided lobby ID.

    The function prompts the user to enter the lobby ID if it is not provided as an argument. It sends
    a POST request to the API URL with the lobby ID and the user ID in the request URL. If the response
    status code is 200, indicating a successful join, the function retrieves the lobby data from the response,
    sets the 'server_id' variable to the lobby ID, and displays a success message along with the lobby ID and
    the current players in the lobby. It then calls the 'start_websocket_listener' function to listen for
    incoming WebSocket messages in the joined lobby. If the response status code is not 200, the function
    handles different error scenarios based on the response status code, displays an appropriate error message,
    and exits the program if necessary.

    Args:
        lobby_id (str, optional): The ID of the lobby to join. If not provided, the user is prompted to enter it.

    Raises:
        - None

    Returns:
        - None
    """
    global server_id, user_id
    if lobby_id is None:
        lobby_id = input("Enter the lobby ID: ")
    response = requests.post(f"{API_URL}/lobby/{lobby_id}/join/{user_id}")
    if response.status_code == 200:
        lobby_data = response.json()
        server_id = lobby_data["id"]
        print("[bold green]Successfully joined the lobby![/bold green]")
        print(f"[bold]Lobby ID:[/bold] {server_id}")
        print("[bold]Current Players:[/bold]")
        for player in lobby_data["players"]:
            print(player["name"])
        start_websocket_listener(lobby_id=server_id)
    elif response.status_code == 403:
        print("[bold red]Lobby is closed. Cannot join.[/bold red]")
        sys.exit()
    elif response.status_code == 404:
        print("[bold red]Lobby or player not found.[/bold red]")
        sys.exit()
    elif response.status_code == 409:
        print("[bold red]Lobby is full. Cannot join.[/bold red]")
        sys.exit()
    else:
        print("[bold red]Failed to join lobby.[/bold red]")
        sys.exit()


# Function to handle incoming WebSocket messages
async def handle_websocket_messages(lobby_id):
    """
    Handle incoming WebSocket messages in the specified lobby.

    The function establishes a WebSocket connection to the server's multicast endpoint using the provided
    lobby ID. It sends the user ID to the server after the connection is established. The function then enters
    a loop to receive and process incoming messages. Each received message is parsed as JSON, and if it contains
    a "message" field, it is printed as a formatted green message. If the message contains a "status" field with
    the value "done", the function checks if the "game_id" field is present in the JSON data. If not, a ValueError
    is raised. Otherwise, the value of "game_id" is assigned to the global variable 'game_id', and the loop is exited.

    Args:
        lobby_id (str): The ID of the lobby to handle WebSocket messages for.

    Raises:
        ValueError: If the "game_id" field is missing in the JSON data when the status is "done".

    Returns:
        - None
    """
    global game_id
    async with websockets.connect(f"ws://localhost:8000/multicast/{lobby_id}") as ws:
        await ws.send(user_id)  # Send the user ID to the server
        running = True
        while running:
            data = await ws.recv()
            json_data = json.loads(data)
            # print(f"[bold green] {json_data} [/bold green]")
            if "message" in json_data:
                print(f"[bold green] {json_data['message']} [/bold green]")
            if "status" in json_data and json_data["status"] == "done":
                if "game_id" not in json_data:
                    raise ValueError("Game ID not found in the JSON data")
                game_id = json_data["game_id"]
                running = False

            sleep(1)



# Function to start the WebSocket listener
def start_websocket_listener(lobby_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handle_websocket_messages(lobby_id))


def get_player_status():
    """
    Retrieve the status of the player in the hangman game.

    The function sends a GET request to the server's status API endpoint to retrieve the current status of the player
    in the hangman game. It expects the `game_id` to be defined and available in the scope where this function is called.
    If the GET request returns a status code of 200, indicating a successful response, the response data is parsed as JSON
    and returned. Otherwise, an appropriate error message is printed, and None is returned.

    Returns:
        dict or None: A dictionary containing the player's status information if available, or None if the request fails
                     or the status code is not 200.
    """
    try:
        response = requests.get(f"{API_URL}/status/{game_id}")
        response.raise_for_status()  # Raise an exception for non-200 status codes
        resp_json = response.json()
        return resp_json
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse response data: {e}")
    return None



def make_guess(game_id, user_id):
    """
    Perform a guessing action in the hangman game.

    The function allows the user to make guesses in the hangman game identified by the provided game ID and user ID.
    It repeatedly prompts the user to enter a character for their guess until the game ends. The function retrieves
    the player status using the `get_player_status` function and checks if it's the user's turn to guess. If so,
    the current word status is displayed, and the user is prompted to enter a character as their guess. The guess
    is sent to the server via a POST request to the guess API endpoint. If the response has a status code of 200,
    the response data is parsed as JSON. The remaining lives of the player and the hangman visual representation
    (if present) are printed. If the player has run out of lives (lives = 0), a corresponding message is printed,
    and the loop is exited. If the response data contains a "Congratulations" message, indicating that the guess
    was correct and the game is won, the victory message and the final word status are printed, and the loop is
    exited. Otherwise, if the guess is incorrect, the loop continues. If the response status code is not 200, an
    error message is printed.

    Args:
        game_id (str): The ID of the hangman game.
        user_id (str): The ID of the player making the guess.

    Returns:
        None
    """
    running = True
    while running:
        player_status = get_player_status()
        if player_status.get("player_status") == user_id:
            current_word_status = player_status.get("word_status")
            print(current_word_status)
            char = input("Make Guess: ")
            GUESS_API_ENDPOINT = f"{API_URL}/guess/{game_id}/{user_id}/{char}"
            response = requests.post(GUESS_API_ENDPOINT)
            if response.status_code == 200:
                data = response.json()
                lives = data.get("lives")
                print(lives if lives else "", "lives")
                if lives == 0:
                    print("You have run out of lives")
                    running = False

                if data.get("hangman"):
                    print(data.get("hangman"))
                if "Congratulations" in data.get("detail", ""):
                    print(data.get('detail'))
                    print("word", data.get("word_status"))
                    running = False  # Break out of the loop if guess is correct

            else:
                print(f"Request failed: {response.text}")
        else:
            ...
        sleep(1)


# Main game loop
def play_game():
    create_player()
    create_or_join_lobby()
    print("GameID", game_id)
    make_guess(game_id, user_id)


if __name__ == "__main__":
    play_game()
