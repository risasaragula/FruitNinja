import cv2
import random
import math
import time


class Game:

    def __init__(self):

        self.score = 0
        self.high_score = 0

        self.lives = 3

        self.combo = 0
        self.last_slice_time = 0
        self.combo_time_limit = 2

        self.fruit_x = 400
        self.fruit_y = 300

        self.fruit_radius = 55

        self.fruit_type = "apple"
        self.fruit_active = False

        self.is_bomb = False

        self.left_piece = False
        self.right_piece = False

        self.slice_time = 0

        self.fruit_speed = 3

        self.first_fruit = True

        self.game_over = False
        self.paused = False

        self.particles = []

    def create_fruit(self, width, height):

        fruits = [
            "apple",
            "orange",
            "watermelon",
            "banana",
            "strawberry",
            "pineapple"
        ]

        bomb_chance = random.randint(1, 5)

        if bomb_chance == 1:

            self.is_bomb = True
            self.fruit_type = "bomb"

        else:

            self.is_bomb = False
            self.fruit_type = random.choice(fruits)

        self.fruit_x = random.randint(
            100,
            width - 100
        )

        self.fruit_y = 120

        self.fruit_active = True

        self.left_piece = False
        self.right_piece = False

        self.first_fruit = False

        self.particles.clear()

    def check_collision(
        self,
        previous_point,
        current_point
    ):

        if self.game_over:
            return

        if self.paused:
            return

        if not self.fruit_active:
            return

        if previous_point is None:
            return

        if current_point is None:
            return

        movement = math.sqrt(
            (
                current_point[0]
                -
                previous_point[0]
            ) ** 2
            +
            (
                current_point[1]
                -
                previous_point[1]
            ) ** 2
        )

        if movement < 25:
            return

        distance = self.point_to_line_distance(
            (
                self.fruit_x,
                self.fruit_y
            ),
            previous_point,
            current_point
        )

        if distance < self.fruit_radius:

            if self.is_bomb:

                self.hit_bomb()

            else:

                self.slice_fruit()

    def point_to_line_distance(
        self,
        point,
        line_start,
        line_end
    ):

        x, y = point

        x1, y1 = line_start

        x2, y2 = line_end

        line_length = math.sqrt(
            (x2 - x1) ** 2
            +
            (y2 - y1) ** 2
        )

        if line_length == 0:

            return math.sqrt(
                (x - x1) ** 2
                +
                (y - y1) ** 2
            )

        t = (
            (x - x1) * (x2 - x1)
            +
            (y - y1) * (y2 - y1)
        ) / (line_length ** 2)

        t = max(
            0,
            min(1, t)
        )

        closest_x = (
            x1
            +
            t * (x2 - x1)
        )

        closest_y = (
            y1
            +
            t * (y2 - y1)
        )

        return math.sqrt(
            (x - closest_x) ** 2
            +
            (y - closest_y) ** 2
        )

    def update_difficulty(self):

        if self.score < 5:

            self.fruit_speed = 3

        elif self.score < 10:

            self.fruit_speed = 4

        elif self.score < 20:

            self.fruit_speed = 5

        elif self.score < 30:

            self.fruit_speed = 6

        else:

            self.fruit_speed = 7

    def create_particles(self):

        self.particles.clear()

        particle_color = self.get_slice_color()

        for i in range(20):

            angle = random.uniform(
                0,
                math.pi * 2
            )

            speed = random.uniform(
                2,
                6
            )

            particle = {
                "x": self.fruit_x,
                "y": self.fruit_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.randint(3, 7),
                "life": random.randint(20, 35),
                "color": particle_color
            }

            self.particles.append(particle)

    def update_particles(self):

        for particle in self.particles:

            particle["x"] += particle["vx"]

            particle["y"] += particle["vy"]

            particle["vy"] += 0.15

            particle["life"] -= 1

        self.particles = [
            particle
            for particle in self.particles
            if particle["life"] > 0
        ]

    def draw_particles(self, frame):

        for particle in self.particles:

            x = int(particle["x"])
            y = int(particle["y"])

            size = particle["size"]

            cv2.circle(
                frame,
                (x, y),
                size,
                particle["color"],
                -1
            )

    def slice_fruit(self):

        current_time = time.time()

        if (
            current_time
            -
            self.last_slice_time
            <=
            self.combo_time_limit
        ):

            self.combo += 1

        else:

            self.combo = 1

        self.last_slice_time = current_time

        self.score += self.combo

        if self.score > self.high_score:

            self.high_score = self.score

        self.update_difficulty()

        self.create_particles()

        self.fruit_active = False

        self.left_piece = True
        self.right_piece = True

        self.slice_time = current_time

    def hit_bomb(self):

        self.lives -= 1

        self.combo = 0

        self.fruit_active = False

        self.left_piece = False
        self.right_piece = False

        self.slice_time = time.time()

        self.particles.clear()

        if self.lives <= 0:

            self.game_over = True

    def miss_fruit(self):

        if self.is_bomb:

            self.fruit_active = False

            self.left_piece = False
            self.right_piece = False

            self.slice_time = time.time()

            return

        self.lives -= 1

        self.combo = 0

        self.fruit_active = False

        self.left_piece = False
        self.right_piece = False

        self.slice_time = time.time()

        if self.lives <= 0:

            self.game_over = True

    def toggle_pause(self):

        if self.game_over:
            return

        self.paused = not self.paused

    def restart(self):

        self.score = 0

        self.lives = 3

        self.combo = 0

        self.last_slice_time = 0

        self.fruit_x = 400
        self.fruit_y = 300

        self.fruit_type = "apple"

        self.fruit_active = False

        self.is_bomb = False

        self.left_piece = False
        self.right_piece = False

        self.slice_time = 0

        self.fruit_speed = 3

        self.first_fruit = True

        self.game_over = False
        self.paused = False

        self.particles.clear()

    def draw_apple(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.circle(
            frame,
            (x, y),
            45,
            (0, 0, 220),
            -1
        )

        cv2.circle(
            frame,
            (x - 15, y - 15),
            7,
            (80, 80, 255),
            -1
        )

        cv2.line(
            frame,
            (x, y - 40),
            (x + 5, y - 60),
            (50, 50, 50),
            5
        )

        cv2.ellipse(
            frame,
            (x + 18, y - 55),
            (15, 7),
            -30,
            0,
            360,
            (0, 180, 0),
            -1
        )

    def draw_orange(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.circle(
            frame,
            (x, y),
            45,
            (0, 140, 255),
            -1
        )

        cv2.circle(
            frame,
            (x - 15, y - 10),
            3,
            (0, 170, 255),
            -1
        )

        cv2.circle(
            frame,
            (x + 15, y + 10),
            3,
            (0, 170, 255),
            -1
        )

        cv2.circle(
            frame,
            (x - 5, y + 15),
            3,
            (0, 170, 255),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 12, y - 45),
            (13, 6),
            -20,
            0,
            360,
            (0, 180, 0),
            -1
        )

    def draw_watermelon(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.circle(
            frame,
            (x, y),
            50,
            (40, 170, 40),
            -1
        )

        cv2.circle(
            frame,
            (x, y),
            42,
            (80, 210, 80),
            -1
        )

        cv2.circle(
            frame,
            (x, y),
            34,
            (40, 50, 220),
            -1
        )

        seeds = [
            (-15, -10),
            (5, -15),
            (18, 0),
            (-8, 12),
            (10, 15)
        ]

        for dx, dy in seeds:

            cv2.ellipse(
                frame,
                (x + dx, y + dy),
                (3, 7),
                0,
                0,
                360,
                (0, 0, 0),
                -1
            )

    def draw_banana(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.ellipse(
            frame,
            (x, y),
            (55, 28),
            -20,
            0,
            180,
            (0, 220, 255),
            -1
        )

        cv2.ellipse(
            frame,
            (x, y),
            (55, 28),
            -20,
            0,
            180,
            (0, 170, 230),
            3
        )

        cv2.circle(
            frame,
            (x - 48, y - 5),
            6,
            (40, 40, 40),
            -1
        )

        cv2.circle(
            frame,
            (x + 48, y + 5),
            6,
            (40, 40, 40),
            -1
        )

    def draw_strawberry(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.circle(
            frame,
            (x, y + 5),
            38,
            (0, 0, 220),
            -1
        )

        cv2.circle(
            frame,
            (x - 22, y - 5),
            22,
            (0, 0, 220),
            -1
        )

        cv2.circle(
            frame,
            (x + 22, y - 5),
            22,
            (0, 0, 220),
            -1
        )

        cv2.ellipse(
            frame,
            (x, y + 30),
            (25, 30),
            0,
            0,
            360,
            (0, 0, 220),
            -1
        )

        cv2.ellipse(
            frame,
            (x, y - 28),
            (30, 10),
            0,
            0,
            360,
            (0, 180, 0),
            -1
        )

        seeds = [
            (-18, 0),
            (0, -5),
            (18, 0),
            (-10, 20),
            (10, 20)
        ]

        for dx, dy in seeds:

            cv2.circle(
                frame,
                (x + dx, y + dy),
                3,
                (0, 220, 255),
                -1
            )

    def draw_pineapple(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.ellipse(
            frame,
            (x, y + 5),
            (38, 50),
            0,
            0,
            360,
            (0, 180, 255),
            -1
        )

        patterns = [
            (-20, -20),
            (0, -20),
            (20, -20),
            (-25, 0),
            (-5, 0),
            (15, 0),
            (-15, 20),
            (5, 20)
        ]

        for dx, dy in patterns:

            cv2.line(
                frame,
                (
                    x + dx - 5,
                    y + dy - 5
                ),
                (
                    x + dx + 5,
                    y + dy + 5
                ),
                (0, 120, 220),
                2
            )

        cv2.line(
            frame,
            (x - 15, y - 40),
            (x - 30, y - 70),
            (0, 180, 0),
            8
        )

        cv2.line(
            frame,
            (x, y - 42),
            (x, y - 75),
            (0, 180, 0),
            8
        )

        cv2.line(
            frame,
            (x + 15, y - 40),
            (x + 30, y - 70),
            (0, 180, 0),
            8
        )

    def draw_bomb(self, frame):

        x = self.fruit_x
        y = self.fruit_y

        cv2.circle(
            frame,
            (x, y),
            45,
            (30, 30, 30),
            -1
        )

        cv2.circle(
            frame,
            (x - 15, y - 15),
            8,
            (100, 100, 100),
            -1
        )

        cv2.line(
            frame,
            (x + 25, y - 30),
            (x + 45, y - 55),
            (50, 50, 50),
            6
        )

        cv2.circle(
            frame,
            (x + 48, y - 58),
            8,
            (0, 140, 255),
            -1
        )

        cv2.circle(
            frame,
            (x + 48, y - 58),
            4,
            (0, 255, 255),
            -1
        )

    def draw_fruit(self, frame):

        if self.is_bomb:

            self.draw_bomb(frame)

            return

        if self.fruit_type == "apple":

            self.draw_apple(frame)

        elif self.fruit_type == "orange":

            self.draw_orange(frame)

        elif self.fruit_type == "watermelon":

            self.draw_watermelon(frame)

        elif self.fruit_type == "banana":

            self.draw_banana(frame)

        elif self.fruit_type == "strawberry":

            self.draw_strawberry(frame)

        elif self.fruit_type == "pineapple":

            self.draw_pineapple(frame)

    def get_slice_color(self):

        if self.fruit_type == "apple":

            return (0, 0, 220)

        elif self.fruit_type == "orange":

            return (0, 140, 255)

        elif self.fruit_type == "watermelon":

            return (40, 50, 220)

        elif self.fruit_type == "banana":

            return (0, 220, 255)

        elif self.fruit_type == "strawberry":

            return (0, 0, 220)

        elif self.fruit_type == "pineapple":

            return (0, 180, 255)

        return (255, 255, 255)

    def draw_apple_halves(
        self,
        frame,
        x,
        y,
        fall
    ):

        color = (0, 0, 220)

        cv2.ellipse(
            frame,
            (x - 28, y + fall),
            (28, 40),
            -15,
            90,
            270,
            color,
            -1
        )

        cv2.ellipse(
            frame,
            (x + 28, y + fall),
            (28, 40),
            15,
            -90,
            90,
            color,
            -1
        )

        cv2.ellipse(
            frame,
            (x - 28, y + fall),
            (18, 30),
            0,
            90,
            270,
            (220, 220, 220),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 28, y + fall),
            (18, 30),
            0,
            -90,
            90,
            (220, 220, 220),
            -1
        )

    def draw_orange_halves(
        self,
        frame,
        x,
        y,
        fall
    ):

        cv2.ellipse(
            frame,
            (x - 28, y + fall),
            (30, 38),
            -10,
            90,
            270,
            (0, 140, 255),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 28, y + fall),
            (30, 38),
            10,
            -90,
            90,
            (0, 140, 255),
            -1
        )

        cv2.circle(
            frame,
            (x - 28, y + fall),
            20,
            (0, 190, 255),
            -1
        )

        cv2.circle(
            frame,
            (x + 28, y + fall),
            20,
            (0, 190, 255),
            -1
        )

    def draw_watermelon_halves(
        self,
        frame,
        x,
        y,
        fall
    ):

        cv2.ellipse(
            frame,
            (x - 27, y + fall),
            (30, 40),
            -15,
            90,
            270,
            (40, 170, 40),
            -1
        )

        cv2.ellipse(
            frame,
            (x - 27, y + fall),
            (24, 34),
            -15,
            90,
            270,
            (40, 50, 220),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 27, y + fall),
            (30, 40),
            15,
            -90,
            90,
            (40, 170, 40),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 27, y + fall),
            (24, 34),
            15,
            -90,
            90,
            (40, 50, 220),
            -1
        )

    def draw_banana_halves(
        self,
        frame,
        x,
        y,
        fall
    ):

        cv2.ellipse(
            frame,
            (x - 30, y + fall),
            (38, 18),
            -25,
            0,
            180,
            (0, 220, 255),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 30, y + fall),
            (38, 18),
            25,
            0,
            180,
            (0, 220, 255),
            -1
        )

    def draw_strawberry_halves(
        self,
        frame,
        x,
        y,
        fall
    ):

        cv2.ellipse(
            frame,
            (x - 25, y + fall),
            (25, 38),
            -15,
            90,
            270,
            (0, 0, 220),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 25, y + fall),
            (25, 38),
            15,
            -90,
            90,
            (0, 0, 220),
            -1
        )

        cv2.circle(
            frame,
            (x - 25, y + fall - 5),
            3,
            (0, 220, 255),
            -1
        )

        cv2.circle(
            frame,
            (x + 25, y + fall + 5),
            3,
            (0, 220, 255),
            -1
        )

    def draw_pineapple_halves(
        self,
        frame,
        x,
        y,
        fall
    ):

        cv2.ellipse(
            frame,
            (x - 25, y + fall),
            (25, 42),
            -10,
            90,
            270,
            (0, 180, 255),
            -1
        )

        cv2.ellipse(
            frame,
            (x + 25, y + fall),
            (25, 42),
            10,
            -90,
            90,
            (0, 180, 255),
            -1
        )

    def draw_sliced_pieces(self, frame):

        if not self.left_piece and not self.right_piece:

            return

        elapsed = (
            time.time()
            -
            self.slice_time
        )

        fall = int(
            elapsed * 180
        )

        x = self.fruit_x
        y = self.fruit_y

        if self.fruit_type == "apple":

            self.draw_apple_halves(
                frame,
                x,
                y,
                fall
            )

        elif self.fruit_type == "orange":

            self.draw_orange_halves(
                frame,
                x,
                y,
                fall
            )

        elif self.fruit_type == "watermelon":

            self.draw_watermelon_halves(
                frame,
                x,
                y,
                fall
            )

        elif self.fruit_type == "banana":

            self.draw_banana_halves(
                frame,
                x,
                y,
                fall
            )

        elif self.fruit_type == "strawberry":

            self.draw_strawberry_halves(
                frame,
                x,
                y,
                fall
            )

        elif self.fruit_type == "pineapple":

            self.draw_pineapple_halves(
                frame,
                x,
                y,
                fall
            )

    def update(self, height):

        if self.game_over:
            return

        if self.paused:
            return

        self.update_particles()

        if not self.fruit_active:
            return

        self.fruit_y += self.fruit_speed

        if self.fruit_y > height - 50:

            self.miss_fruit()

        if (
            self.combo > 0
            and
            time.time()
            -
            self.last_slice_time
            >
            self.combo_time_limit
        ):

            self.combo = 0

    def draw(self, frame):

        cv2.putText(
            frame,
            f"Score: {self.score}",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            3
        )

        cv2.putText(
            frame,
            f"High Score: {self.high_score}",
            (30, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Lives: {self.lives}",
            (30, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255, 255, 255),
            3
        )

        if self.combo > 1:

            cv2.putText(
                frame,
                f"COMBO x{self.combo}",
                (30, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 255),
                3
            )

        if self.paused:

            cv2.putText(
                frame,
                "PAUSED",
                (270, 300),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 255, 255),
                5
            )

            cv2.putText(
                frame,
                "Press P to Continue",
                (250, 360),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                3
            )

            self.draw_particles(frame)

            return

        if self.game_over:

            cv2.putText(
                frame,
                "GAME OVER",
                (250, 300),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 0, 255),
                5
            )

            cv2.putText(
                frame,
                f"Final Score: {self.score}",
                (270, 360),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (255, 255, 255),
                3
            )

            cv2.putText(
                frame,
                f"High Score: {self.high_score}",
                (270, 400),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (0, 255, 255),
                3
            )

            cv2.putText(
                frame,
                "Press R to Restart",
                (250, 460),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                3
            )

            self.draw_particles(frame)

            return

        if self.fruit_active:

            self.draw_fruit(frame)

        self.draw_sliced_pieces(frame)

        self.draw_particles(frame)

    def check_new_fruit(
        self,
        width,
        height
    ):

        if self.paused:
            return

        if self.first_fruit:

            self.create_fruit(
                width,
                height
            )

            return

        if self.game_over:
            return

        if not self.fruit_active:

            elapsed = (
                time.time()
                -
                self.slice_time
            )

            if elapsed > 0.6:

                self.left_piece = False

                self.right_piece = False

                if self.lives > 0:

                    self.create_fruit(
                        width,
                        height
                    )