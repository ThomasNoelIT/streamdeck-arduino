import sys
import os

# Permet d'importer src/ depuis n'importe où (script ou .exe)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui import StreamDeckApp

if __name__ == "__main__":
    app = StreamDeckApp()
    app.mainloop()