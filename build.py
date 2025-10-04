
import os
import sys
import subprocess
import shutil


def build_game():
    """Build the game executable."""
    print("=" * 60)
    print("Building Maze Adventure Game")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Check if pygame is installed
    try:
        import pygame
        print("✓ Pygame found")
    except ImportError:
        print("✗ Pygame not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])

    # Clean previous builds
    print("\nCleaning previous builds...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("maze_game.spec"):
        os.remove("maze_game.spec")

    # PyInstaller command
    print("\nBuilding executable...")

    pyinstaller_args = [
        "main.py",
        "--name=MazeAdventure",
        "--onefile",
        "--windowed",
        "--icon=NONE",  # Add icon file path if available
        "--add-data=maze_game.db:.",  # Include database
        "--hidden-import=pygame",
        "--hidden-import=sqlite3",
        "--clean"
    ]

    # Add platform-specific separator
    if sys.platform == "win32":
        pyinstaller_args[5] = "--add-data=maze_game.db;."

    try:
        subprocess.check_call(["pyinstaller"] + pyinstaller_args)
        print("\n" + "=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print(f"\nExecutable location: dist/MazeAdventure{'.exe' if sys.platform == 'win32' else ''}")
        print("\nYou can now distribute the executable from the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_game()