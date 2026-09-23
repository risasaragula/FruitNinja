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

        self.fruit_radius = 55
        self.fruit_speed = 3

        self.fruits = []
        self.sliced_pieces = []
        self.particles = []

        self.fruit_active = False
        self.first_fruit = True

        self.game_over = False
        self.paused = False

        self.max_fruits = 2

        self.fruit_x = 400
        self.fruit_y = 300
        self.fruit_type = "apple"
        self.is_bomb = False

        self.left_piece = False
        self.right_piece = False
        self.slice_time = 0

    def create_fruit(self, width, height):

        fruits = [
            "apple",
            "orange",
            "watermelon",
            "banana",
            "strawberry",
            "pineapple"
        ]

        is_bomb = random.randint(1, 6) == 1

        if is_bomb:
            fruit_type = "bomb"
        else:
            fruit_type = random.choice(fruits)

        fruit = {
            "x": random.randint(100, width - 100),
            "y": 120,
            "type": fruit_type,
            "bomb": is_bomb,
            "radius": self.fruit_radius,
            "speed": self.fruit_speed + random.uniform(-0.5, 1.2)
        }

        self.fruits.append(fruit)

        self.fruit_active = True
        self.first_fruit = False

    def update_difficulty(self):

        if self.score < 5:

            self.fruit_speed = 3
            self.max_fruits = 2

        elif self.score < 10:

            self.fruit_speed = 4
            self.max_fruits = 2

        elif self.score < 20:

            self.fruit_speed = 5
            self.max_fruits = 3

        elif self.score < 30:

            self.fruit_speed = 6
            self.max_fruits = 3

        else:

            self.fruit_speed = 7
            self.max_fruits = 4

    def check_collision(
        self,
        previous_point,
        current_point
    ):

        if self.game_over:
            return

        if self.paused:
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

        hit_fruit = None

        for fruit in self.fruits:

            distance = self.point_to_line_distance(
                (
                    fruit["x"],
                    fruit["y"]
                ),
                previous_point,
                current_point
            )

            if distance < fruit["radius"]:

                hit_fruit = fruit
                break

        if hit_fruit is None:
            return

        if hit_fruit["bomb"]:

            self.hit_bomb(hit_fruit)

        else:

            self.slice_fruit(hit_fruit)

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

    def create_particles(self, fruit):

        particle_color = self.get_slice_color(
            fruit["type"]
        )

        self.particles.clear()

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
                "x": fruit["x"],
                "y": fruit["y"],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.randint(3, 7),
                "life": random.randint(20, 35),
                "color": particle_color
            }

            self.particles.append(
                particle
            )

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

            cv2.circle(
                frame,
                (
                    int(particle["x"]),
                    int(particle["y"])
                ),
                particle["size"],
                particle["color"],
                -1
            )

    def slice_fruit(self, fruit):

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

        self.create_particles(
            fruit
        )

        self.sliced_pieces.append(
            {
                "x": fruit["x"],
                "y": fruit["y"],
                "type": fruit["type"],
                "time": current_time
            }
        )

        if fruit in self.fruits:

            self.fruits.remove(
                fruit
            )

        self.fruit_active = (
            len(self.fruits) > 0
        )

    def hit_bomb(self, fruit):

        self.lives -= 1

        self.combo = 0

        if fruit in self.fruits:

            self.fruits.remove(
                fruit
            )

        self.fruit_active = (
            len(self.fruits) > 0
        )

        self.particles.clear()

        if self.lives <= 0:

            self.game_over = True

    def miss_fruit(self, fruit):

        if fruit["bomb"]:

            if fruit in self.fruits:

                self.fruits.remove(
                    fruit
                )

            self.fruit_active = (
                len(self.fruits) > 0
            )

            return

        self.lives -= 1

        self.combo = 0

        if fruit in self.fruits:

            self.fruits.remove(
                fruit
            )

        self.fruit_active = (
            len(self.fruits) > 0
        )

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

        self.fruits.clear()

        self.sliced_pieces.clear()

        self.particles.clear()

        self.fruit_active = False

        self.first_fruit = True

        self.fruit_speed = 3

        self.max_fruits = 2

        self.game_over = False

        self.paused = False

    def draw_apple(
        self,
        frame,
        x,
        y
    ):

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

    def draw_orange(
        self,
        frame,
        x,
        y
    ):

        cv2.circle(
            frame,
            (x, y),
            45,
            (0, 140, 255),
            -1
        )

        for dx, dy in [
            (-15, -10),
            (15, 10),
            (-5, 15)
        ]:

            cv2.circle(
                frame,
                (x + dx, y + dy),
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

    def draw_watermelon(
        self,
        frame,
        x,
        y
    ):

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

    def draw_banana(
        self,
        frame,
        x,
        y
    ):

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

    def draw_strawberry(
        self,
        frame,
        x,
        y
    ):

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

    def draw_pineapple(
        self,
        frame,
        x,
        y
    ):

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

    def draw_bomb(
        self,
        frame,
        x,
        y
    ):

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

    def draw_fruit(
        self,
        frame,
        fruit
    ):

        x = int(fruit["x"])
        y = int(fruit["y"])

        if fruit["bomb"]:

            self.draw_bomb(
                frame,
                x,
                y
            )

            return

        if fruit["type"] == "apple":

            self.draw_apple(
                frame,
                x,
                y
            )

        elif fruit["type"] == "orange":

            self.draw_orange(
                frame,
                x,
                y
            )

        elif fruit["type"] == "watermelon":

            self.draw_watermelon(
                frame,
                x,
                y
            )

        elif fruit["type"] == "banana":

            self.draw_banana(
                frame,
                x,
                y
            )

        elif fruit["type"] == "strawberry":

            self.draw_strawberry(
                frame,
                x,
                y
            )

        elif fruit["type"] == "pineapple":

            self.draw_pineapple(
                frame,
                x,
                y
            )

    def get_slice_color(
        self,
        fruit_type
    ):

        colors = {
            "apple": (0, 0, 220),
            "orange": (0, 140, 255),
            "watermelon": (40, 50, 220),
            "banana": (0, 220, 255),
            "strawberry": (0, 0, 220),
            "pineapple": (0, 180, 255)
        }

        return colors.get(
            fruit_type,
            (255, 255, 255)
        )

    def draw_sliced_pieces(
        self,
        frame
    ):

        current_time = time.time()

        remaining = []

        for piece in self.sliced_pieces:

            elapsed = (
                current_time
                -
                piece["time"]
            )

            if elapsed > 0.6:

                continue

            x = int(piece["x"])

            y = int(
                piece["y"]
                +
                elapsed * 180
            )

            color = self.get_slice_color(
                piece["type"]
            )

            cv2.ellipse(
                frame,
                (x - 25, y),
                (25, 38),
                -15,
                90,
                270,
                color,
                -1
            )

            cv2.ellipse(
                frame,
                (x + 25, y),
                (25, 38),
                15,
                -90,
                90,
                color,
                -1
            )

            cv2.ellipse(
                frame,
                (x - 25, y),
                (15, 25),
                0,
                90,
                270,
                (220, 220, 220),
                -1
            )

            cv2.ellipse(
                frame,
                (x + 25, y),
                (15, 25),
                0,
                -90,
                90,
                (220, 220, 220),
                -1
            )

            remaining.append(
                piece
            )

        self.sliced_pieces = remaining

    def update(
        self,
        height
    ):

        if self.game_over:
            return

        if self.paused:
            return

        self.update_particles()

        for fruit in self.fruits[:]:

            fruit["y"] += fruit["speed"]

            if fruit["y"] > height - 50:

                self.miss_fruit(
                    fruit
                )

        self.fruit_active = (
            len(self.fruits) > 0
        )

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

    def draw(
        self,
        frame
    ):

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

        for fruit in self.fruits:

            self.draw_fruit(
                frame,
                fruit
            )

        self.draw_sliced_pieces(
            frame
        )

        self.draw_particles(
            frame
        )

    def check_new_fruit(
        self,
        width,
        height
    ):

        if self.paused:
            return

        if self.game_over:
            return

        self.update_difficulty()

        if self.first_fruit:

            self.create_fruit(
                width,
                height
            )

            self.create_fruit(
                width,
                height
            )

            return

        if len(self.fruits) < self.max_fruits:

            spawn_chance = (
                0.025
                +
                self.score * 0.001
            )

            if random.random() < spawn_chance:

                self.create_fruit(
                    width,
                    height
                )