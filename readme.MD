# Hangman Game

This project implements a multiplayer hangman game using FastAPI, websockets, and requests library.

## Installation

`cd app`

Install the dependencies:

`pip install -r requirements.txt`

## Running the Server

Start the FastAPI server In Debug Mode:

`uvicorn main:app --reload`

Start the Fastapi server in PROD mode

`uvicorn main:app`

if you encounter any problem while running app with this command: `uvicorn main:app`

Instead use This:
`python -m uvicorn main:app`
## Running the Client
- Open a new terminal or command prompt window.
- Change into the project directory if you're not already in it:
  `cd app`
- run the hangman game client:
 `python hangman_client.py`

Repeat step 4 in additional terminal or command prompt windows to run multiple clients and play the game in multiplayer mode.