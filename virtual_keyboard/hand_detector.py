import cv2
import mediapipe as mp

class HandDetector:
    """Kelas untuk enkapsulasi deteksi tangan MediaPipe."""
    def __init__(self, max_hands=1, detection_con=0.7, track_con=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hand_landmarks(self, img, draw=True):
        """Mencari landmark tangan pada sebuah gambar."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        landmark_list = []
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([id, cx, cy])
        
        return landmark_list