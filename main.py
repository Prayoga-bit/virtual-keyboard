from virtual_keyboard.app import VirtualKeyboardApp
import os

if __name__ == "__main__":
    # Tentukan path ke aset
    FONT_PATH = os.path.join("assets", "fonts", "arial.ttf")
    WORD_LIST_PATH = os.path.join("assets", "kamus_kata.txt")

    # Cek apakah file font ada
    if not os.path.exists(FONT_PATH):
        print(f"Error: Font file not found at '{FONT_PATH}'")
        print("Please download 'arial.ttf' and place it in the 'assets/fonts/' directory.")
    else:
        app = VirtualKeyboardApp(font_path=FONT_PATH, word_list_path=WORD_LIST_PATH)
        app.run()