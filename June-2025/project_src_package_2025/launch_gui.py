import sys
import os
from gui.app import main

# Ensure root directory (where gui/ lives) is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    print("Current directory:", os.getcwd())
    print("sys.path:", sys.path)
    main()
