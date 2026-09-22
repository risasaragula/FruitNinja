import cv2
import winsound

from hand_tracking import HandTracker
from game import Game


def play_slice_sound():
    winsound.Beep(1000, 80)


def play_bomb_sound():
    winsound.Beep(200, 300)


def play_miss_sound():
    winsound.Beep(400, 150)


def play_game_over_sound():
    winsound.Beep(250, 400)
    winsound.Beep(150, 500)


def play_restart_sound():
    winsound.Beep(700, 100)


def play_pause_sound():
    winsound.Beep(600, 100)


def draw_start_screen(frame):

    height, width, _ = frame.shape

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, height),
        (15, 15, 15),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.78,
        frame,
        0.22,
        0
    )

    title_scale = min(width, height) / 500

    if title_scale < 1:
        title_scale = 1

    title_x = width // 2 - 300
    title_y = int(height * 0.25)

    cv2.putText(
        frame,
        "GESTURE FRUIT NINJA",
        (title_x, title_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        title_scale,
        (0, 255, 255),
        4
    )

    subtitle_x = width // 2 - 190
    subtitle_y = int(height * 0.34)

    cv2.putText(
        frame,
        "Computer Vision Edition",
        (subtitle_x, subtitle_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (210, 210, 210),
        2
    )

    instruction_y = int(height * 0.48)

    cv2.putText(
        frame,
        "Move your index finger to slice fruits",
        (width // 2 - 250, instruction_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Avoid the bombs!",
        (width // 2 - 120, instruction_y + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 165, 255),
        2
    )

    button_width = 360
    button_height = 70

    button_x1 = width // 2 - button_width // 2
    button_y1 = int(height * 0.66)

    button_x2 = width // 2 + button_width // 2
    button_y2 = button_y1 + button_height

    cv2.rectangle(
        frame,
        (button_x1, button_y1),
        (button_x2, button_y2),
        (35, 35, 35),
        -1
    )

    cv2.rectangle(
        frame,
        (button_x1, button_y1),
        (button_x2, button_y2),
        (0, 255, 255),
        3
    )

    cv2.putText(
        frame,
        "PRESS SPACE TO START",
        (width // 2 - 150, button_y1 + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    controls_y = button_y2 + 45

    cv2.putText(
        frame,
        "P  -  Pause",
        (width // 2 - 90, controls_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (220, 220, 220),
        2
    )

    cv2.putText(
        frame,
        "Q  -  Quit",
        (width // 2 - 80, controls_y + 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (220, 220, 220),
        2
    )


hand_tracker = HandTracker()

game = Game()

cap = cv2.VideoCapture(0)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)

cv2.namedWindow(
    "Gesture Fruit Ninja",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Gesture Fruit Ninja",
    1200,
    675
)

game_started = False


while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(
        frame,
        1
    )

    height, width, _ = frame.shape

    if not game_started:

        draw_start_screen(frame)

        cv2.imshow(
            "Gesture Fruit Ninja",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):

            game_started = True

            game.restart()

            play_restart_sound()

        if key == ord("q"):

            break

        continue

    previous_position = (
        hand_tracker.previous_point
    )

    finger_position = (
        hand_tracker.get_finger_position(
            frame
        )
    )

    hand_tracker.draw_trail(frame)

    old_score = game.score

    old_lives = game.lives

    old_game_over = game.game_over

    old_is_bomb = game.is_bomb

    game.check_collision(
        previous_position,
        finger_position
    )

    if game.score > old_score:

        play_slice_sound()

    game.update(height)

    if game.lives < old_lives:

        if old_is_bomb:

            play_bomb_sound()

        else:

            play_miss_sound()

    if game.game_over and not old_game_over:

        play_game_over_sound()

    game.draw(frame)

    game.check_new_fruit(
        width,
        height
    )

    hand_tracker.update_previous_point()

    cv2.imshow(
        "Gesture Fruit Ninja",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("p"):

        game.toggle_pause()

        play_pause_sound()

        hand_tracker.previous_point = None

    if key == ord("r") and game.game_over:

        game.restart()

        play_restart_sound()

    if key == ord("q"):

        break


cap.release()

cv2.destroyAllWindows()

hand_tracker.close()