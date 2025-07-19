import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def draw_text_with_font(img, text, position, font_path, font_size, color):
    """
    Menggambar teks pada gambar OpenCV menggunakan font TTF dari Pillow.
    """
    # Konversi gambar OpenCV (BGR) ke gambar Pillow (RGBA)
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Muat font kustom
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font tidak ditemukan di {font_path}. Menggunakan font default.")
        font = ImageFont.load_default()
        
    # Gambar teks
    draw.text(position, text, font=font, fill=color)
    
    # Konversi kembali ke format OpenCV
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)