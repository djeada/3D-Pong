import vtk


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, actor, renderer, paddle1, paddle2, score1, score2):
        self.AddObserver("KeyPressEvent", self.key_press_event)
        self.actor = actor
        self.renderer = renderer
        self.paddle1 = paddle1
        self.paddle2 = paddle2
        self.score1 = score1
        self.score2 = score2
        self.timer_id = None
        self.direction = [0.01, 0.01, 0.0]
        self.score = [0, 0]

    def OnKeyPress(self):
        # This method gets called on 'KeyPressEvent'
        # By overriding it, we can change the default behavior of the 'w' key,
        # which normally toggles between wireframe and solid view
        key = self.GetInteractor().GetKeySym()
        if key != "w":
            # Call parent's key press method only if pressed key is not 'w'
            super().OnKeyPress()

    def reset(self):
        self.actor.SetPosition(0, 0, 0)
        self.score1.SetInput(str(self.score[0]))
        self.score2.SetInput(str(self.score[1]))

    def key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        position_left_paddle = list(self.paddle1.GetPosition())
        position_right_paddle = list(self.paddle2.GetPosition())

        # Control for the left paddle
        if key == "Up":
            position_right_paddle[1] += 0.1
        elif key == "Down":
            position_right_paddle[1] -= 0.1

        # Control for the right paddle
        if key == "w":
            position_left_paddle[1] += 0.1

        elif key == "s":
            position_left_paddle[1] -= 0.1

        self.paddle1.SetPosition(position_left_paddle[0], position_left_paddle[1], 0)
        self.paddle2.SetPosition(position_right_paddle[0], position_right_paddle[1], 0)

    def execute(self, obj, event):
        position = list(self.actor.GetPosition())
        new_position = [
            position[0] + self.direction[0],
            position[1] + self.direction[1],
            0,
        ]

        # Ball radius
        ball_radius = 0.02

        # Paddle range
        paddle_range = 0.2

        # Paddle positions
        paddle1_pos = self.paddle1.GetPosition()[1]
        paddle2_pos = self.paddle2.GetPosition()[1]

        # Check if ball is about to hit paddle1 (left paddle)
        if (
            -0.9 <= new_position[0] - ball_radius <= -0.89
            and paddle1_pos - paddle_range
            <= new_position[1]
            <= paddle1_pos + paddle_range
            and self.direction[0] < 0
        ):
            self.direction[0] = -self.direction[0]
        # Check if ball is about to hit paddle2 (right paddle)
        elif (
            0.89 <= new_position[0] + ball_radius <= 0.9
            and paddle2_pos - paddle_range
            <= new_position[1]
            <= paddle2_pos + paddle_range
            and self.direction[0] > 0
        ):
            self.direction[0] = -self.direction[0]

        # Check if ball is about to hit top or bottom wall
        if new_position[1] - ball_radius < -1.0:
            new_position[1] = -1.0 + ball_radius
            self.direction[1] = -self.direction[1]
        elif new_position[1] + ball_radius > 1.0:
            new_position[1] = 1.0 - ball_radius
            self.direction[1] = -self.direction[1]

        # Check if ball is about to hit left wall
        if new_position[0] - ball_radius < -1.0:
            new_position[0] = -1.0 + ball_radius
            self.direction[0] = -self.direction[0]
            self.score[1] += 1
            self.score2.SetInput(str(self.score[1]))  # Update score2 display
        # Check if ball is about to hit right wall
        elif new_position[0] + ball_radius > 1.0:
            new_position[0] = 1.0 - ball_radius
            self.direction[0] = -self.direction[0]
            self.score[0] += 1
            self.score1.SetInput(str(self.score[0]))  # Update score1 display

        self.actor.SetPosition(new_position[0], new_position[1], 0)
        self.GetInteractor().GetRenderWindow().Render()


def create_paddle():
    paddle_source = vtk.vtkCubeSource()
    paddle_source.SetXLength(0.02)
    paddle_source.SetYLength(0.4)
    paddle_source.SetZLength(0.02)

    paddle_mapper = vtk.vtkPolyDataMapper()
    paddle_mapper.SetInputConnection(paddle_source.GetOutputPort())

    paddle_actor = vtk.vtkActor()
    paddle_actor.SetMapper(paddle_mapper)

    return paddle_actor


def create_text_actor(position):
    text_actor = vtk.vtkTextActor()
    text_actor.SetPosition(position)
    text_property = text_actor.GetTextProperty()
    text_property.SetFontSize(24)
    text_property.BoldOn()
    text_actor.SetInput("0")

    return text_actor


def create_border(x1, y1, z1, x2, y2, z2):
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(x1, y1, z1)
    line_source.SetPoint2(x2, y2, z2)

    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputConnection(line_source.GetOutputPort())

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)

    return line_actor


# Create a sphere (the ball)
ball_source = vtk.vtkSphereSource()
ball_source.SetRadius(0.02)
ball_source.SetPhiResolution(20)
ball_source.SetThetaResolution(20)

ball_mapper = vtk.vtkPolyDataMapper()
ball_mapper.SetInputConnection(ball_source.GetOutputPort())

ball_actor = vtk.vtkActor()
ball_actor.SetMapper(ball_mapper)

# Create paddles
paddle1 = create_paddle()
paddle1.SetPosition(-0.9, 0, 0)
paddle2 = create_paddle()
paddle2.SetPosition(0.9, 0, 0)

# Create score display
score1 = create_text_actor((200, 560))  # Player 1 score positioned to the left
score2 = create_text_actor((600, 560))  # Player 2 score positioned to the right


# Create a renderer
renderer = vtk.vtkRenderer()

# Add the sphere actor, paddles, and score display to the renderer
renderer.AddActor(ball_actor)
renderer.AddActor(paddle1)
renderer.AddActor(paddle2)
renderer.AddActor(score1)
renderer.AddActor(score2)

border1 = create_border(-1.0, -1.0, 0.0, -1.0, 1.0, 0.0)
border2 = create_border(-1.0, 1.0, 0.0, 1.0, 1.0, 0.0)
border3 = create_border(1.0, 1.0, 0.0, 1.0, -1.0, 0.0)
border4 = create_border(1.0, -1.0, 0.0, -1.0, -1.0, 0.0)

renderer.AddActor(border1)
renderer.AddActor(border2)
renderer.AddActor(border3)
renderer.AddActor(border4)

# Create a rendering window
render_window = vtk.vtkRenderWindow()

# Add the renderer to the rendering window
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)  # Set window size

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

style = KeyPressInteractorStyle(ball_actor, renderer, paddle1, paddle2, score1, score2)
interactor.SetInteractorStyle(style)

interactor.Initialize()
interactor.CreateRepeatingTimer(1)
interactor.AddObserver("TimerEvent", style.execute)

# Start the visualization
interactor.Start()
