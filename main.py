import tkinter as tk
from src.ui.image_generator_ui import ImageGeneratorUI

def main():
    root = tk.Tk()
    app = ImageGeneratorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()   