# 3D Pong Game

This project is a 3D implementation of the classic game Pong using the Visualization Toolkit (VTK). It is a two-player game where each player controls a paddle to hit the ball and prevent it from reaching their goal. The score is updated in real-time.

![Game Screenshot](https://github.com/djeada/3D-Pong/assets/37275728/de3d4952-6504-4171-868c-b7b6d80455b6)

## Features
- 3D Real-Time Rendering: Utilizes VTK to create an immersive 3D game environment.
- Two-Player Functionality: Play with a friend! Keyboard controls allow for two players to compete.
- Collision Detection: Never miss a hit with the accurate collision detection between the ball, paddles, and game boundaries.
- Real-Time Scoring: Keep track of the competition with the in-game real-time scoring system.

## Controls
- Player 1: Use the 'w' key to move the paddle up and the 's' key to move it down.
- Player 2: Use the 'Up' arrow key to move the paddle up and the 'Down' arrow key to move it down.

## Requirements

- The Visualization Toolkit (VTK) should be installed and set up properly in your Python environment.

You can set up a virtual environment and install all project dependencies in the following way:

```
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

## Usage

After completing the installation steps, you can run the game using the following command:

```bash
$ python src/main.py
```

## Contributing
We welcome contributions to this guide! If you would like to contribute, please create a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
