import cv2
from .hand_detector import HandDetector
from .ui_manager import UIManager

class VirtualKeyboardApp:
    def __init__(self, font_path, word_list_path):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        
        self.detector = HandDetector()
        self.ui = UIManager(font_path)
        
        self.final_text = ""
        self.shift_active = False

    def run(self):
        while True:
            success, img = self.cap.read()
            if not success:
                break
            
            img = cv2.flip(img, 1)

            # 1. Deteksi tangan
            landmarks = self.detector.find_hand_landmarks(img)
            
            # 2. Proses input dan dapatkan karakter yang diketik
            typed_char, img = self.ui.process_input(img, landmarks)

            # 3. Logika pengetikan
            if typed_char:
                if typed_char == "<-":
                    self.final_text = self.final_text[:-1]
                elif typed_char == "Shift":
                    self.shift_active = not self.shift_active
                elif typed_char in ["Tab", "Ctrl"]: # Placeholder
                    pass
                else:
                    char_to_add = typed_char
                    if not self.shift_active:
                        char_to_add = char_to_add.lower()
                    self.final_text += char_to_add
                    self.shift_active = False # Shift hanya berlaku untuk satu huruf

            # 4. Gambar seluruh UI
            img = self.ui.draw_all(img, self.final_text)
            
            # Tampilkan status Shift
            if self.shift_active:
                cv2.putText(img, "SHIFT", (1050, 40), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

            cv2.imshow("Virtual Keyboard", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()