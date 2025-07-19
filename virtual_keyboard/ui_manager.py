import cv2
import time
from .utils import draw_text_with_font

class KeyboardButton:
    """Merepresentasikan tombol individual dengan efek frosted glass."""
    def __init__(self, pos, text, size, font_path):
        self.pos = pos
        self.text = text
        self.size = size
        self.font_path = font_path

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        
        # Efek "Frosted Glass"
        if x >= 0 and y >= 0 and x + w < img.shape[1] and y + h < img.shape[0]:
            roi = img[y:y+h, x:x+w]
            blurred_roi = cv2.GaussianBlur(roi, (21, 21), 0)
            
            overlay = img.copy()
            cv2.rectangle(overlay, self.pos, (x + w, y + h), (255, 255, 255), cv2.FILLED)
            
            # Gabungkan dengan alpha untuk transparansi
            alpha = 0.3
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
            img[y:y+h, x:x+w] = blurred_roi

        # Border tombol
        cv2.rectangle(img, self.pos, (x + w, y + h), (200, 200, 200), 2)
        
        # Menggambar teks dengan font Arial
        font_size = 30 if len(self.text) == 1 else 20
        text_color = (0, 0, 0) # Warna teks hitam agar kontras dengan putih
        
        # Kalkulasi posisi teks agar di tengah
        # (Fungsi Pillow memerlukan pendekatan berbeda untuk centering)
        text_x, text_y = x + 15, y + 15  # Posisi disesuaikan
        if len(self.text) == 1:
            text_x += 15
            
        img_with_text = draw_text_with_font(img, self.text, (text_x, text_y), self.font_path, font_size, text_color)
        return img_with_text

    def is_over(self, cursor_pos):
        x, y = self.pos
        w, h = self.size
        return x < cursor_pos[0] < x + w and y < cursor_pos[1] < y + h

class UIManager:
    """Mengelola semua elemen UI dan interaksi pengguna."""
    def __init__(self, font_path):
        self.font_path = font_path
        self.keys_layout = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        ]
        self.buttons = self._create_keyboard_buttons()
        self.hovered_button = None
        self.hover_start_time = 0
        self.DWELL_TIME = 0.6  # Detik untuk menahan kursor sebelum 'klik'

    def _create_keyboard_buttons(self):
        button_list = []
        key_w, key_h = 80, 80
        key_gap = 10

        for i, row in enumerate(self.keys_layout):
            for j, key_char in enumerate(row):
                x = 50 + j * (key_w + key_gap)
                y = 50 + i * (key_h + key_gap)
                button_list.append(KeyboardButton((x, y), key_char, (key_w, key_h), self.font_path))

        # Baris bawah (fungsional)
        y_bottom = 50 + 3 * (key_h + key_gap)
        button_list.append(KeyboardButton((50, y_bottom), "Shift", (125, key_h), self.font_path))
        button_list.append(KeyboardButton((185, y_bottom), " ", (445, key_h), self.font_path))
        button_list.append(KeyboardButton((640, y_bottom), "<-", (125, key_h), self.font_path))
        button_list.append(KeyboardButton((775, y_bottom), "Tab", (125, key_h), self.font_path))

        return button_list

    def draw_all(self, img, text_buffer):
        # Gambar semua tombol
        for button in self.buttons:
            img = button.draw(img)
        
        # Gambar area display teks
        display_x, display_y, display_w, display_h = 50, 420, 855, 70
        cv2.rectangle(img, (display_x, display_y), (display_x + display_w, display_y + display_h), (200, 200, 200), 2)
        img = draw_text_with_font(img, text_buffer, (display_x + 15, display_y + 10), self.font_path, 40, (255, 255, 255))
        return img

    def process_input(self, img, landmarks):
        """
        Memproses input berdasarkan posisi jari dengan metode Hover & Dwell.
        Mengembalikan karakter yang diketik, jika ada.
        """
        typed_char = None
        
        if not landmarks:
            self.hovered_button = None
            return typed_char, img
        
        # Kursor adalah ujung jari telunjuk (landmark #8)
        cursor_pos = (landmarks[8][1], landmarks[8][2])
        cv2.circle(img, cursor_pos, 10, (255, 0, 255), cv2.FILLED)

        # Cek apakah kursor berada di atas tombol
        currently_over = None
        for button in self.buttons:
            if button.is_over(cursor_pos):
                currently_over = button
                break
        
        # Logika Hover & Dwell
        if currently_over:
            if self.hovered_button is not currently_over:
                # Kursor pindah ke tombol baru, reset timer
                self.hovered_button = currently_over
                self.hover_start_time = time.time()
            else:
                # Kursor masih di tombol yang sama, cek durasi
                dwell_duration = time.time() - self.hover_start_time
                
                # Visualisasi Dwell Time
                progress = min(dwell_duration / self.DWELL_TIME, 1.0)
                radius = int(progress * 30)
                cv2.circle(img, cursor_pos, radius, (0, 255, 0, 128), 4)

                if dwell_duration >= self.DWELL_TIME:
                    # Klik terdeteksi!
                    typed_char = self.hovered_button.text
                    self.hovered_button = None # Reset setelah klik
        else:
            # Kursor tidak di atas tombol mana pun
            self.hovered_button = None
            
        return typed_char, img