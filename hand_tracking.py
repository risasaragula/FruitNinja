import cv2
import mediapipe as mp


class HandTracker:

    def __init__(self):

        BaseOptions = mp.tasks.BaseOptions

        HandLandmarker = (
            mp.tasks.vision.HandLandmarker
        )

        HandLandmarkerOptions = (
            mp.tasks.vision.HandLandmarkerOptions
        )

        VisionRunningMode = (
            mp.tasks.vision.RunningMode
        )

        options = HandLandmarkerOptions(

            base_options=BaseOptions(
                model_asset_path="hand_landmarker.task"
            ),

            running_mode=(
                VisionRunningMode.VIDEO
            ),

            num_hands=1
        )

        self.landmarker = (
            HandLandmarker.create_from_options(
                options
            )
        )

        self.timestamp = 0


        self.previous_point = None

        self.current_point = None


        self.trail = []


    def get_finger_position(self, frame):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Increase timestamp
        self.timestamp += 1

        # Detect hand
        result = self.landmarker.detect_for_video(
            mp_image,
            self.timestamp
        )


        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            # Landmark 8 = index fingertip
            index_finger = hand[8]

            height, width, _ = frame.shape

            x = int(
                index_finger.x * width
            )

            y = int(
                index_finger.y * height
            )

            self.current_point = (
                x,
                y
            )

            # Add to trail
            self.trail.append(
                self.current_point
            )

            # Keep last 15 points
            if len(self.trail) > 15:

                self.trail.pop(0)

            return self.current_point


        self.current_point = None

        self.trail.clear()

        return None


    def update_previous_point(self):

        self.previous_point = (
            self.current_point
        )


    def draw_trail(self, frame):

        if self.current_point is None:

            return

        # Draw trail
        for i in range(
            1,
            len(self.trail)
        ):

            cv2.line(

                frame,

                self.trail[i - 1],

                self.trail[i],

                (0, 255, 255),

                5
            )

        # Draw fingertip
        cv2.circle(

            frame,

            self.current_point,

            10,

            (0, 255, 0),

            -1
        )


    def close(self):

        self.landmarker.close()