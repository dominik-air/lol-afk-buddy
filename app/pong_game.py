from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
                            ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint


class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            speedup = 1.1
            offset = 0.11 * Vector(0, ball.center_y - self.center_y)
            ball.velocity = speedup * (offset - ball.velocity)

class PongBall(Widget):
    velocity_x = NumericProperty(.1)
    velocity_y = NumericProperty(.1)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    # definiuje pole, które później będzie zainicjalizowane
    # inicjalizacja jest wartością "None", ale tak na prawdę chodzi
    # tutaj gównie od wyspecyfikowanie typu, aby kivy odpowiednio
    # obeszło się z tą zminną.

    # PongGame properties (#1)
    ball = ObjectProperty(None) # inicjalizacja klasy PongBall poprzez plik kv
    player1 = ObjectProperty(None) # inicjalizacja klasy PongPaddle poprzez kv
    player2 = ObjectProperty(None) # tak jak wyżej
    scorea = StringProperty("0")
    scoreb = StringProperty("0")

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center # property from kv file
        self.ball.velocity = vel # property from the def of the class

    def update(self, dt):
        self.ball.move()

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        # bounce off left and right
        if (self.ball.x < 0) or (self.ball.right > self.width):
            self.ball.velocity_x *= -1

        # went of to a side to score point?
        if self.ball.x < self.player1.width/2:
            self.player2.score += 1
            self.scoreb = str(self.player2.score) 
            self.serve_ball(vel=(4, 0))
        if self.ball.x + self.ball.width > self.width - self.player2.width/2:
            self.player1.score += 1
            self.scorea = str(self.player1.score)
            self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):
        if touch.x < self.width/3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width/3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
