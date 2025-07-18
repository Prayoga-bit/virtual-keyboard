import cv2
import math
import mediapipe as mp

class KeyboardButton:
    """Kelas untuk merepresentasikan satu tombol pada keyboard virtual."""
    def __init__(self, pos, text, size=(80, 80)):
        self.pos = pos
        self.text = text
        self.size = size

    def draw(self, img, alpha=0.5, text_color=(255, 255, 255)):
        """Menggambar tombol pada gambar yang diberikan."""
        x, y = self.pos
        w, h = self.size
        
        # Gambar persegi panjang transparan sebagai latar belakang tombol
        overlay = img.copy()
        cv2.rectangle(overlay, self.pos, (x + w, y + h), (50, 50, 50), cv2.FILLED)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # Tambahkan outline/border
        cv2.rectangle(img, self.pos, (x + w, y + h), (200, 200, 200), 3)

        # Tambahkan teks pada tombol
        font = cv2.FONT_HERSHEY_PLAIN
        text_size = cv2.getTextSize(self.text, font, 2, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(img, self.text, (text_x, text_y), font, 2, text_color, 2)
    
    def is_over(self, cursor_pos):
        """Mengecek apakah posisi kursor berada di atas tombol ini."""
        x, y = self.pos
        w, h = self.size
        cx, cy = cursor_pos
        return x < cx < x + w and y < cy < y + h

class VirtualKeyboardApp:
    """Kelas utama untuk aplikasi keyboard virtual."""
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)  # Lebar frame
        self.cap.set(4, 720)   # Tinggi frame

        # Inisialisasi MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

        # Tata letak keyboard
        self.keys_layout = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        ]
        self.buttons = self._create_keyboard_buttons()

        # Variabel status
        self.final_text = ""
        self.click_cooldown = 15  # Frame cooldown untuk mencegah double click
        self.cooldown_counter = 0
        self.is_caps = False
        
        # Muat kamus untuk rekomendasi
        self.word_list = self._load_word_list('Indonesia_ID.txt')

    def _load_word_list(self, filename):
        """Memuat daftar kata dari file teks."""
        try:
            with open(filename, 'r') as f:
                return [line.strip().lower() for line in f]
        except FileNotFoundError:
            print(f"Peringatan: File kamus '{filename}' tidak ditemukan. Fitur rekomendasi tidak akan aktif.")
            return []

    def _create_keyboard_buttons(self):
        """Membuat objek-objek KeyboardButton berdasarkan layout."""
        button_list = []
        for i, row in enumerate(self.keys_layout):
            for j, key_char in enumerate(row):
                # Posisi x dan y untuk setiap tombol
                x = 100 + j * 90
                y = 100 + i * 90
                button_list.append(KeyboardButton((x, y), key_char))
        
        # Tambah tombol fungsional
        button_list.append(KeyboardButton((100, 370), " ", size=(620, 80)))
        button_list.append(KeyboardButton((730, 370), "<-", size=(180, 80))) # Backspace
        button_list.append(KeyboardButton((920, 370), "CAPS", size=(170, 80))) # Caps Lock
        
        return button_list

    def draw_ui(self, img):
        """Menggambar semua elemen UI pada frame."""
        # Gambar semua tombol
        for button in self.buttons:
            button.draw(img)

        # Gambar area tampilan teks
        cv2.rectangle(img, (100, 480), (1090, 550), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (100, 480), (1090, 550), (200, 200, 200), 3)
        cv2.putText(img, self.final_text, (110, 525), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        
        # Tampilkan rekomendasi kata
        self.draw_word_suggestions(img)

    def draw_word_suggestions(self, img):
        """Mencari dan menampilkan rekomendasi kata."""
        words = self.final_text.split(' ')
        if not self.final_text or self.final_text.endswith(' '):
            return

        current_word = words[-1].lower()
        if not current_word:
            return

        suggestions = [word for word in self.word_list if word.startswith(current_word)][:3] # Ambil 3 rekomendasi
        
        for i, suggestion in enumerate(suggestions):
            pos_x = 100 + i * 220
            pos_y = 570
            cv2.rectangle(img, (pos_x, pos_y), (pos_x + 200, pos_y + 50), (80, 80, 80), cv2.FILLED)
            cv2.putText(img, suggestion, (pos_x + 10, pos_y + 35), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    
    def run(self):
        """Menjalankan loop utama aplikasi."""
        while True:
            success, img = self.cap.read()
            if not success:
                break
            
            # Balik gambar agar menjadi seperti cermin
            img = cv2.flip(img, 1)

            # Deteksi tangan
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            all_landmarks = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    for lm in hand_landmarks.landmark:
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        all_landmarks.append([cx, cy])

            # Gambar UI
            self.draw_ui(img)

            # Proses input jika tangan terdeteksi
            if all_landmarks and self.cooldown_counter == 0:
                # Ambil posisi ujung jari telunjuk (landmark 8) dan tengah (landmark 12)
                p_index = all_landmarks[8]
                p_middle = all_landmarks[12]

                # Gambar kursor di ujung jari telunjuk
                cv2.circle(img, (p_index[0], p_index[1]), 15, (255, 0, 255), cv2.FILLED)

                for button in self.buttons:
                    if button.is_over((p_index[0], p_index[1])):
                        # Highlight tombol yang sedang ditunjuk
                        button.draw(img, alpha=0.2, text_color=(0, 255, 0))
                        
                        # Hitung jarak antara jari telunjuk dan jari tengah untuk deteksi "klik"
                        distance = math.hypot(p_middle[0] - p_index[0], p_middle[1] - p_index[1])
                        
                        if distance < 40: # Jarak threshold untuk "klik"
                            # Aksi berdasarkan tombol yang diklik
                            if button.text == "<-":
                                self.final_text = self.final_text[:-1]
                            elif button.text == "CAPS":
                                self.is_caps = not self.is_caps
                            elif button.text == " ":
                                self.final_text += " "
                            else:
                                char_to_add = button.text
                                self.final_text += char_to_add if self.is_caps else char_to_add.lower()
                            
                            self.cooldown_counter = self.click_cooldown # Reset cooldown
                            button.draw(img, alpha=0.1, text_color=(0, 0, 255)) # Feedback klik

            # Update cooldown counter
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1

            cv2.imshow("Virtual Keyboard", img)

            # Keluar jika tombol 'q' ditekan
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = VirtualKeyboardApp()
    app.run()