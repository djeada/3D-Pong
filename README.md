# 3D Pong Game

This project is a 3D implementation of the classic game Pong using the Visualization Toolkit (VTK). It is a two-player game where each player controls a paddle to hit the ball and prevent it from reaching their goal. The score is updated in real-time.

![Game Screenshot](https://github.com/djeada/3D-Pong/assets/37275728/de3d4952-6504-4171-868c-b7b6d80455b6)

## Features
- **3D Real-Time Rendering**: Utilizes VTK to create an immersive 3D game environment.
- **Two-Player Functionality**: Play with a friend! Keyboard controls allow for two players to compete.
- **Collision Detection**: Never miss a hit with the accurate collision detection between the ball, paddles, and game boundaries.
- **Real-Time Scoring**: Keep track of the competition with the in-game real-time scoring system.

## Controls
- **Player 1**: Use the `w` key to move the paddle up and the `s` key to move it down.
- **Player 2**: Use the `Up` arrow key to move the paddle up and the `Down` arrow key to move it down.

## Installation

### For Developers

To work with the source code and manage dependencies, follow these steps:

1. **Clone the Repository**: First, clone the repository to your local machine.

    ```bash
    $ git clone https://github.com/djeada/3D-Pong.git
    $ cd 3D-Pong
    ```

2. **Set Up a Virtual Environment**: It's a good practice to use a virtual environment to manage dependencies.

    ```bash
    $ virtualenv env
    $ source env/bin/activate
    ```

3. **Install Dependencies**: Install the required Python packages listed in the `requirements.txt` file.

    ```bash
    $ pip install -r requirements.txt
    ```

4. **Verify VTK Installation**: Ensure that VTK is installed correctly by running a simple VTK script or checking the installation.

    ```bash
    $ python -c "import vtk; print(vtk.VTK_VERSION)"
    ```

5. **Run the Game**: After setting up everything, you can run the game using the following command:

    ```bash
    $ python src/main.py
    ```

### For Normal Users

For users who just want to play the game without diving into the source code, follow these steps:

1. **Download the Executable**: Go to the [Releases](https://github.com/yourusername/3D-Pong/releases) page of the GitHub repository.

2. **Select the Latest Release**: Find the latest release and download the executable file appropriate for your operating system (e.g., Windows, macOS, Linux).

3. **Run the Executable**:
    - **Windows**: Double-click the `.exe` file to start the game.
    - **macOS/Linux**: Open a terminal, navigate to the directory containing the downloaded file, and run the following command:

      ```bash
      $ chmod +x 3D-Pong
      $ ./3D-Pong
      ```
      
## Contributing
We welcome contributions to this guide! If you would like to contribute, please create a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
