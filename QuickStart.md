# Quick Start Guide 🚀

Get the Maze Adventure Game up and running in 3 minutes!

## For End Users (Playing the Game)

If you received a `.exe` (Windows) or `.app` (macOS) file:

1. **Double-click the executable**
2. **That's it!** The game will start immediately

No Python or other installations needed!

## For Developers (Setting Up From Source)

### Windows

```batch
# 1. Install Python 3.8+ from python.org

# 2. Open Command Prompt and navigate to game folder
cd path\to\maze_game

# 3. Install dependencies
pip install pygame

# 4. Run the game
python main.py
```

### macOS/Linux

```bash
# 1. Open Terminal and navigate to game folder
cd path/to/maze_game

# 2. Install dependencies
pip3 install pygame

# 3. Run the game
python3 main.py
```

## Building Your Own Executable

### One-Command Build

```bash
# Install build tool
pip install pyinstaller

# Build executable
python build.py
```

The executable will be in the `dist/` folder.

### Manual Build

**Windows:**
```batch
pyinstaller main.py --name=MazeAdventure --onefile --windowed --add-data="maze_game.db;."
```

**macOS/Linux:**
```bash
pyinstaller main.py --name=MazeAdventure --onefile --windowed --add-data="maze_game.db:."
```

## First Time Setup

When you first run the game:

1. Press **1** on the main menu
2. Press **1** again to login as guest
3. Press **1** to start playing!

## Controls Cheat Sheet

### In Menu
- `1-6` = Select menu options
- `ESC` = Quit

### In Game
- `Arrow Keys` or `WASD` = Move
- `ESC` or `P` = Pause
- `R` = Restart (when game over)

### In Editor
- `Left Click` = Paint tile
- `Right Click` = Erase tile
- `1-5` = Select tool (Wall, Path, Start, Exit, Enemy)
- `C` = Clear grid
- `S` = Save maze
- `ESC` = Exit editor

## Troubleshooting

**"Python is not recognized"**
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation

**"No module named pygame"**
```bash
pip install pygame
```

**Game crashes on start**
- Delete `maze_game.db` file and try again
- Make sure you have Python 3.8 or higher

**Executable won't run (Windows)**
- Windows Defender might block it
- Right-click → Properties → Unblock

## Project File Checklist

Make sure you have all these files:

```
maze_game/
├── main.py              ✅ Entry point
├── requirements.txt     ✅ Dependencies list
├── build.py            ✅ Build script
└── src/
    ├── game.py         ✅ Main game logic
    ├── player.py       ✅ Player class
    ├── enemy.py        ✅ Enemy AI
    ├── maze_generator.py ✅ Maze algorithms
    ├── database.py     ✅ Database manager
    ├── ui.py           ✅ UI components
    ├── editor.py       ✅ Maze editor
    └── utils/
        └── constants.py ✅ Configuration
```

Missing files? Download them from the complete project package.

## Next Steps

1. ✅ Run the game
2. ✅ Complete a few levels
3. ✅ Try the maze editor
4. ✅ Customize your character skin
5. ✅ Build your own executable
6. ✅ Share with friends!

## Need More Help?

Check the full **README.md** for:
- Detailed feature documentation
- Complete API reference
- Advanced customization options
- Database schema
- Code architecture

---

**Enjoy the game! 🎮**