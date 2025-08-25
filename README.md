# Project AURA 🧿

## The Intelligent Audio Co-pilot for Gamers

Project AURA is a desktop application that uses computer vision to understand a player's focus and intelligently manages in-game audio to provide a competitive advantage and a more immersive experience.

---

### ## Current Status: **Phase 2 - Prototyping** 👨‍💻

This project is in the very early stages of development. The current version consists of the basic application window and UI skeleton. The core AI and computer vision features are not yet implemented.

---

### ## MVP Feature Set (The Blueprint)

The goal for our Minimum Viable Product (MVP) is to deliver the "Focus Mode" feature. The planned features are:

1.  **Simple Onboarding:** A clean, one-time setup screen for permissions.
2.  **Automatic Focus Detection:** The core engine that activates "Focus Mode" automatically.
3.  **Minimalist In-Game Overlay:** A simple on-screen indicator to show when AURA is active.
4.  **"Before & After" Demo Mode:** An in-app feature to instantly demonstrate the audio effect.
5.  **Manual Override:** A global hotkey to toggle the service on and off.

---

### ## Technology Stack

* **Language:** Python
* **UI Framework:** PyQt6
* **Computer Vision:** OpenCV & MediaPipe (planned)

---

### ## How to Run

1.  **Clone the repository (once it's on GitHub):**
    `git clone <your-repo-link>`
2.  **Create a virtual environment:**
    `python -m venv venv`
    `source venv/bin/activate`  // On Windows, use `venv\Scripts\activate`
3.  **Install dependencies:**
    `pip install PyQt6`
4.  **Run the application:**
    `python main.py`