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
        (20, 20, 20),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.75,
        frame,
        0.25,
        0
    )

    cv2.putText(
        frame,
        "FRUIT NINJA",
        (width // 2 - 220, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (0, 255, 255),
        5
    )

    cv2.putText(
        frame,
        "Slice the fruits!",
        (width // 2 - 150, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 255, 255),
        3
    )

    cv2.putText(
        frame,
        "Avoid the bombs!",
        (width // 2 - 160, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 150, 255),
        3
    )

    cv2.putText(
        frame,
        "PRESS SPACE TO START",
        (width // 2 - 230, 390),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3
    )

    cv2.putText(
        frame,
        "Press P to Pause",
        (width // 2 - 120, 430),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Press Q to Quit",
        (width // 2 - 120, 470),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (200, 200, 200),
        2
    )


hand_tracker = HandTracker()

game = Game()

cap = cv2.VideoCapture(0)

game_started = False


while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape

    if not game_started:

        draw_start_screen(frame)

        cv2.imshow(
            "Fruit Ninja",
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

    previous_position = hand_tracker.previous_point

    finger_position = (
        hand_tracker.get_finger_position(frame)
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
        "Fruit Ninja",
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