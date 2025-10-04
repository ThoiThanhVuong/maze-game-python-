# Installation Guide - Maze Adventure Game

Complete step-by-step instructions for setting up and running the game.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation from Source](#installation-from-source)
3. [Running from Executable](#running-from-executable)
4. [Building Your Own Executable](#building-your-own-executable)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### For Running from Source

**Required:**
- Python 3.8 or higher
- pip (Python package installer)
- 100 MB free disk space

**Operating Systems:**
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, Fedora, etc.)

### For Running from Executable

**No prerequisites!** Just download and double-click.

---

## Installation from Source

### Step 1: Install Python

#### Windows
1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.8 or higher
3. Run installer
4. **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"
6. Verify installation:
   ```cmd
   python --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
```

Verify:
```bash
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

#### Linux (Fedora)
```bash
sudo dnf install python3 python3-pip
python3 --version
```

### Step 2: Download Project Files

**Option A: Download ZIP**
1. Download the project ZIP file
2. Extract to a folder (e.g., `C:\Games\maze_game` or `~/Games/maze_game`)

**Option B: Git Clone** (if available)
```bash
git clone <repository-url>
cd maze_game
```

### Step 3: Set Up Project Structure

Navigate to project folder:
```bash
cd path/to/maze_game
```

Run setup script:
```bash
python setup_project.py
```

This creates all necessary folders and files.

### Step 4: Organize Files

Place files in correct locations:

```
maze_game/
├── main.py                 ← Root
├── requirements.txt        ← Root
├── build.py               ← Root
├── maze_game.spec         ← Root
└── src/
    ├── __init__.py        ← Auto-created
    ├── game.py            ← Place here
    ├── player.py          ← Place here
    ├── enemy.py           ← Place here
    ├── maze_generator.py  ← Place here
    ├── database.py        ← Place here
    ├── ui.py              ← Place here
    ├── editor.py          ← Place here
    └── utils/
        ├── __init__.py    ← Auto-created
        └── constants.py   ← Place here
```

### Step 5: Install Dependencies

#### Windows
```cmd
pip install pygame
```

Or install all at once:
```cmd
pip install -r requirements.txt
```

#### macOS/Linux
```bash
pip3 install pygame
```

Or:
```bash
pip3 install -r requirements.txt
```

### Step 6: Verify Installation

Check if pygame is installed:
```python
python -c "import pygame; print(pygame.version.ver)"
```

Should output version like: `2.5.2`

### Step 7: Run the Game

#### Windows
```cmd
python main.py
```

#### macOS/Linux
```bash
python3 main.py
```

**Success!** The game window should open.

---

## Running from Executable

### Windows

1. **Download** `MazeAdventure.exe`
2. **Optional**: Create a shortcut on desktop
3. **Double-click** to run

**First-time Windows security prompt:**
- Click "More info"
- Click "Run anyway"
- This is normal for unsigned executables

### macOS

1. **Download** `MazeAdventure.app`
2. **Move** to Applications folder (optional)
3. **Right-click** → Open (first time only)
4. Click "Open" in security prompt

**If "App is damaged" error appears:**
```bash
xattr -cr /path/to/MazeAdventure.app
```

### Linux

1. **Download** `MazeAdventure` binary
2. **Make executable:**
   ```bash
   chmod +x MazeAdventure
   ```
3. **Run:**
   ```bash
   ./MazeAdventure
   ```

---

## Building Your Own Executable

### Method 1: Automated Build (Easiest)

```bash
# Install PyInstaller
pip install pyinstaller

# Run build script
python build.py
```

**Output:** `dist/MazeAdventure.exe` (Windows) or `dist/MazeAdventure` (Linux/macOS)

### Method 2: Manual PyInstaller

#### Windows
```cmd
pyinstaller main.py ^
    --name=MazeAdventure ^
    --onefile ^
    --windowed ^
    --add-data="maze_game.db;." ^
    --hidden-import=pygame ^
    --clean
```

#### macOS/Linux
```bash
pyinstaller main.py \
    --name=MazeAdventure \
    --onefile \
    --windowed \
    --add-data="maze_game.db:." \
    --hidden-import=pygame \
    --clean
```

#### Using spec file
```bash
pyinstaller maze_game.spec
```

### Method 3: cx_Freeze

Create `setup_cxfreeze.py`:

```python
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["pygame", "sqlite3"],
    "include_files": ["maze_game.db", "src/"]
}

setup(
    name="MazeAdventure",
    version="1.0",
    description="2D Maze Adventure Game",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")]
)
```

Build:
```bash
pip install cx_Freeze
python setup_cxfreeze.py build
```

### Method 4: Nuitka (Fastest Runtime)

```bash
pip install nuitka
python -m nuitka --standalone --onefile --windows-disable-console main.py
```

---

## Troubleshooting

### Common Issues

#### "Python is not recognized"

**Problem:** Python not in system PATH

**Solution (Windows):**
1. Search for "Environment Variables"
2. Click "Environment Variables"
3. Under "System variables", find "Path"
4. Click "Edit" → "New"
5. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X`
6. Restart command prompt

**Solution (macOS/Linux):**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="/usr/local/bin:$PATH"
```

#### "No module named pygame"

**Problem:** Pygame not installed

**Solution:**
```bash
pip install pygame
# or
pip3 install pygame
```

If still fails:
```bash
python -m pip install pygame
```

#### "Permission denied" (Linux/macOS)

**Problem:** File not executable

**Solution:**
```bash
chmod +x MazeAdventure
```

#### Game crashes on startup

**Problem:** Missing dependencies or corrupted database

**Solution:**
1. Delete `maze_game.db` (will be recreated)
2. Reinstall pygame:
   ```bash
   pip uninstall pygame
   pip install pygame
   ```
3. Check Python version: `python --version` (need 3.8+)

#### "DLL load failed" (Windows)

**Problem:** Missing Visual C++ redistributables

**Solution:**
1. Download VC Redist from Microsoft
2. Install both x86 and x64 versions

#### Slow performance

**Solutions:**
1. Reduce FPS in `constants.py`:
   ```python
   FPS = 30  # Instead of 60
   ```
2. Reduce maze size:
   ```python
   MAX_MAZE_SIZE = 31  # Instead of 51
   ```
3. Close other applications
4. Update graphics drivers

#### PyInstaller build fails

**Common fixes:**
```bash
# Update PyInstaller
pip install --upgrade pyinstaller

# Clear cache
pyinstaller --clean main.py

# Try without --onefile
pyinstaller main.py --windowed
```

#### Executable won't run on other computers

**Problem:** Missing system dependencies

**Solution:**
- Windows: Include VC Redist with your distribution
- macOS: Sign and notarize the app
- Linux: Build on oldest supported OS version

#### "Access denied" when saving (Windows)

**Problem:** Running from protected folder

**Solution:**
- Don't run from `C:\Program Files`
- Use user folder: `C:\Users\YourName\Games`

#### Black screen on startup

**Solutions:**
1. Update graphics drivers
2. Disable hardware acceleration
3. Try running in windowed mode

#### Database errors

**Solutions:**
```bash
# Delete and recreate
rm maze_game.db
python main.py  # Will create new database
```

---

## Platform-Specific Notes

### Windows

**Antivirus False Positives:**
- Windows Defender may flag PyInstaller executables
- Add exception: Settings → Update & Security → Windows Security → Virus & threat protection → Manage settings → Add exclusion

**Windows 7:**
- Requires Visual C++ 2015-2019 Redistributable
- Download from Microsoft website

### macOS

**Gatekeeper:**
- First run: Right-click → Open
- Or disable: `sudo spctl --master-disable` (not recommended)

**Code Signing** (for distribution):
```bash
codesign --force --deep --sign - MazeAdventure.app
```

### Linux

**Dependencies** (if needed):
```bash
# Ubuntu/Debian
sudo apt install python3-pygame

# Fedora
sudo dnf install python3-pygame

# Arch
sudo pacman -S python-pygame
```

**Desktop Entry** (optional):
Create `~/.local/share/applications/maze-adventure.desktop`:
```ini
[Desktop Entry]
Name=Maze Adventure
Exec=/path/to/MazeAdventure
Icon=/path/to/icon.png
Type=Application
Categories=Game;
```

---

## Verification Steps

After installation, verify everything works:

### Checklist
- [ ] Game window opens
- [ ] Can navigate menu
- [ ] Can login as guest
- [ ] Can start game
- [ ] Player moves with arrow keys
- [ ] Enemies appear and move
- [ ] Can reach exit and complete level
- [ ] Health bar updates
- [ ] Score increases
- [ ] Can pause/resume
- [ ] Can access leaderboard
- [ ] Can open maze editor
- [ ] Can save/load custom mazes

### Test Script

Run this to verify installation:
```python
import sys
import pygame

print(f"Python version: {sys.version}")
print(f"Pygame version: {pygame.version.ver}")
print("✓ All dependencies working!")
```

---

## Getting Help

If you still have issues:

1. **Check logs:**
   - Look for error messages in console
   - Windows: Run from cmd to see errors
   - macOS/Linux: Run from terminal

2. **System info:**
   ```bash
   python --version
   pip list | grep pygame
   ```

3. **Clean reinstall:**
   ```bash
   pip uninstall pygame
   pip cache purge
   pip install pygame
   ```

4. **Test basic pygame:**
   ```python
   import pygame
   pygame.init()
   screen = pygame.display.set_mode((640, 480))
   print("Pygame works!")
   pygame.quit()
   ```

---

## Next Steps

After successful installation:

1. Read **QUICKSTART.md** for gameplay guide
2. Read **README.md** for full documentation
3. Try building your own executable
4. Customize the game in `constants.py`
5. Create custom mazes in the editor

**Enjoy the game! 🎮**