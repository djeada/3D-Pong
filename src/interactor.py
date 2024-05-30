import vtk
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, actor, renderer, paddle1, paddle2, score1, score2, game_config):
        super().__init__()
        self.actor = actor
        self.renderer = renderer
        self.paddle1 = paddle1
        self.paddle2 = paddle2
        self.score1 = score1
        self.score2 = score2
        self.game_config = game_config
        self.timer_id = None
        self.direction = [0.01, 0.01, 0.0]
        self.score = [0, 0]
        self.time_elapsed = 0
        self.AddObserver("KeyPressEvent", self.key_press_event)
        logging.info("KeyPressInteractorStyle initialized.")

    def reset(self):
        self.actor.SetPosition(0, 0, 0)
        self.update_score_display()
        logging.info("Game reset. Ball position and scores reset.")

    def update_score_display(self):
        self.score1.SetInput(str(self.score[0]))
        self.score2.SetInput(str(self.score[1]))
        logging.debug(
            f"Scores updated. Player 1: {self.score[0]}, Player 2: {self.score[1]}"
        )

    def key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        logging.debug(f"Key pressed: {key}")
        self.move_paddles(key)

    def move_paddles(self, key):
        position_left_paddle = list(self.paddle1.GetPosition())
        position_right_paddle = list(self.paddle2.GetPosition())

        if key == "Up":
            position_right_paddle[1] += 0.1
        elif key == "Down":
            position_right_paddle[1] -= 0.1
        elif key == "w":
            position_left_paddle[1] += 0.1
        elif key == "s":
            position_left_paddle[1] -= 0.1

        self.paddle1.SetPosition(position_left_paddle[0], position_left_paddle[1], 0)
        self.paddle2.SetPosition(position_right_paddle[0], position_right_paddle[1], 0)
        logging.debug(
            f"Paddle positions updated. Left: {position_left_paddle}, Right: {position_right_paddle}"
        )

    def execute(self, obj, event):
        self.time_elapsed += 1
        if self.time_elapsed % self.game_config["speed_increase_interval"] == 0:
            self.increase_ball_speed()

        new_position = self.calculate_new_position()
        self.check_collisions(new_position)
        self.update_ball_position(new_position)
        self.GetInteractor().GetRenderWindow().Render()

    def increase_ball_speed(self):
        self.direction[0] *= self.game_config["speed_multiplier"]
        self.direction[1] *= self.game_config["speed_multiplier"]
        logging.debug(f"Ball speed increased. New direction: {self.direction}")

    def calculate_new_position(self):
        position = list(self.actor.GetPosition())
        new_position = [
            position[0] + self.direction[0],
            position[1] + self.direction[1],
            0,
        ]
        logging.debug(f"Calculated new ball position: {new_position}")
        return new_position

    def check_collisions(self, new_position):
        ball_radius = 0.02
        paddle_range = 0.2

        self.check_paddle_collision(new_position, ball_radius, paddle_range)
        self.check_wall_collision(new_position, ball_radius)

    def check_paddle_collision(self, new_position, ball_radius, paddle_range):
        paddle1_pos = self.paddle1.GetPosition()[1]
        paddle2_pos = self.paddle2.GetPosition()[1]

        if (
            -0.9 <= new_position[0] - ball_radius <= -0.89
            and paddle1_pos - paddle_range
            <= new_position[1]
            <= paddle1_pos + paddle_range
            and self.direction[0] < 0
        ):
            self.direction[0] = -self.direction[0]
            logging.debug("Ball hit left paddle.")

        elif (
            0.89 <= new_position[0] + ball_radius <= 0.9
            and paddle2_pos - paddle_range
            <= new_position[1]
            <= paddle2_pos + paddle_range
            and self.direction[0] > 0
        ):
            self.direction[0] = -self.direction[0]
            logging.debug("Ball hit right paddle.")

    def check_wall_collision(self, new_position, ball_radius):
        if new_position[1] - ball_radius < -1.0:
            new_position[1] = -1.0 + ball_radius
            self.direction[1] = -self.direction[1]
            logging.debug("Ball hit bottom wall.")
        elif new_position[1] + ball_radius > 1.0:
            new_position[1] = 1.0 - ball_radius
            self.direction[1] = -self.direction[1]
            logging.debug("Ball hit top wall.")

        if new_position[0] - ball_radius < -1.0:
            new_position[0] = -1.0 + ball_radius
            self.direction[0] = -self.direction[0]
            self.score[1] += 1
            self.update_score_display()
            logging.info("Ball hit left wall. Player 2 scored.")
        elif new_position[0] + ball_radius > 1.0:
            new_position[0] = 1.0 - ball_radius
            self.direction[0] = -self.direction[0]
            self.score[0] += 1
            self.update_score_display()
            logging.info("Ball hit right wall. Player 1 scored.")

    def update_ball_position(self, new_position):
        self.actor.SetPosition(new_position[0], new_position[1], 0)
        logging.debug(f"Ball position updated: {new_position}")
