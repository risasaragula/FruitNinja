# FruitNinja

A Python-based Fruit Ninja game controlled using hand gestures with OpenCV and MediaPipe.

## Features

- Control the game using hand movements
- Slice fruits using your index finger
- Real-time hand tracking using the webcam
- Score tracking
- Bombs and lives
- Combo system
- Fruit slicing effects

## Technologies Used

- Python
- OpenCV
- MediaPipe
- Pygame
- NumPy

## How It Works

The webcam captures the player's hand movements.

MediaPipe detects the hand and tracks the index finger.

The index finger is used as the slicing point to interact with fruits on the screen.

When the finger touches a fruit, the fruit is sliced and the score is updated.

## How to Run

Install the required packages:

    pip install opencv-python mediapipe pygame numpy

Then run:

    python main.py

Make sure your webcam is connected and allow camera access when prompted.

## Author

Risa Saragula
