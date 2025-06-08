# Pygame Music Player

This project is a Python-based music player that emulates the classic iPod interface using Pygame.

## Features

- Music library scanning and database management
- iPod Classic-like UI
- Playback controls (play, pause, next, previous)
- Volume control
- Shuffle and repeat modes
- Browsing by artist, album, and song

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url.git
    cd pygame-music-player
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Place your music files:**
    Create a `music` folder in the project root or ensure your system's default music directories (`~/Music`, `/media`, `/mnt`) are accessible.
5.  **Run the application:**
    ```bash
    python src/main.py
    ```

## Project Structure

```
pygame-music-player/
├── src/
│   ├── main.py         # Main application, UI, event handling
│   ├── database.py     # SQLite database interaction, music library scanning
│   └── playback.py     # Music playback logic, controls
├── assets/
│   └── fonts/          # Font files (e.g., Arial.ttf)
├── music/              # Optional: Local music directory
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Usage

- Use arrow keys (Up/Down) or W/S to navigate menus.
- Press Enter or Space to select an item.
- Press Escape or Backspace to go back.
- In the "Now Playing" screen:
    - Left/A for previous song.
    - Right/D for next song.
    - P to play/pause.
    - V to open volume control (then Up/Down).

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
