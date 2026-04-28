# Simple Lyric Display (SLD)

![CI Status](https://github.com/ks-fl/simple-lyric-display/actions/workflows/ci.yml/badge.svg)

A lightweight, modern lyric display for Linux desktops. Syncs local `.lrc` files with any music player via MPRIS2.

![App Screenshot](https://via.placeholder.com/600x400?text=Simple+Lyric+Display+Screenshot)

## 🎯 Core Concepts

- **Local First:** 100% reliance on local `.lrc` files. No unreliable web searches or broken APIs.
- **Universal Support:** Works with any MPRIS2-compliant player (Audacious, Strawberry, Rhythmbox, Firefox, Spotify, etc.).
- **Distraction-Free:** A frameless, transparent overlay that stays on top and auto-scrolls with your music.

## ✨ Features

- **Precise Sync:** Follows playback position with millisecond precision.
- **Auto-Scrolling:** Automatically jumps to the current line and keeps it visible.
- **Visual Highlighting:** Active lines are highlighted with theme-aware colors.
- **Customizable Aesthetics:** 
  - Change font family and size.
  - Choose from premium presets (Nord, Solarized, GitHub, etc.).
  - Variable window opacity.
- **Smart Window Management:**
  - Remembers position and size across sessions.
  - "Always on Top" toggle.
  - Drag-and-move from anywhere in the window.
  - System tray integration for quick access.

## 🛠 Tech Stack

- **Language:** Python 3.14+
- **GUI Framework:** PySide6 (Qt for Python)
- **IPC:** D-Bus (via `gdbus`)

## 🚀 Getting Started

### Prerequisites

- **Python 3.14+**
- **gdbus** (standard on most Linux distributions)
- A desktop environment with a **compositor** (Cinnamon, GNOME, KDE, etc.) for transparency.
- An MPRIS2-compatible music player.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ks-fl/simple-lyric-display.git
   cd simple-lyric-display
   ```

2. Install everything:
   ```bash
   make install
   ```
   *Note: This will automatically create a virtual environment (`.venv`) and install all dependencies.*

3. Run the application:
   ```bash
   make run
   ```

### 📦 Building a Standalone Binary

To create a single executable that doesn't require a Python environment:

1. Build the binary:
   ```bash
   make build
   ```

2. Your binary will be ready at `dist/simple-lyric-display`.

## ⚙️ Configuration

Settings are saved automatically upon exit. You can access settings by right-clicking the window or using the system tray icon.

Config file: `~/.config/simple-lyric-display/config.json`

## 📄 License

MIT License
