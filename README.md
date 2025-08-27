# Project AURA 🧿

### The Intelligent Audio Co-pilot for Gamers

Project AURA is a smart desktop application for Windows that uses your webcam to analyze your level of focus and automatically adjusts your system's audio in real-time. It's designed to provide a competitive advantage and a more immersive experience in games by making crucial audio cues, like enemy footsteps, easier to hear during chaotic moments.



---
## ✨ Core Features

* **Real-time Focus Detection:** Uses a hybrid OpenCV and Dlib AI model to track facial landmarks and calculate a "Focus Score" based on your Eye Aspect Ratio (EAR).
* **Automatic Audio Ducking:** Intelligently lowers the volume of other applications (games, music, etc.) when you're focused, and restores it when you relax.
* **Live Webcam Feed:** Provides a visual of what the AI is seeing, including the detected facial landmarks.
* **Tunable Sensitivity:** On-screen sliders allow you to adjust the AI's sensitivity to match your specific webcam, lighting, and personal preferences.
* **Built-in Demo:** A demo button lets you instantly hear the effect of the audio processing.

---
## 🛠️ Technology Stack

* **Language:** Python 3.11
* **UI Framework:** PyQt6
* **Computer Vision:** OpenCV & Dlib
* **Windows Audio Control:** pycaw

---
## 🚀 Getting Started

Follow these instructions to get Project AURA running on your local machine.

### **1. Prerequisites**

This project has dependencies that require specific build tools on Windows.
* **Microsoft C++ Build Tools:** You must have the MSVC++ 14.0 or greater build tools. You can get them here: [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). During installation, select the "Desktop development with C++" workload.
* **CMake:** You must have the full CMake application installed and added to your system's PATH. You can get it here: [CMake Downloads](https://cmake.org/download/). During installation, be sure to select the option **"Add CMake to the system PATH for all users."**

### **2. Installation**

1.  **Clone the repository:**
    ```
    git clone [https://github.com/your-username/project-aura.git](https://github.com/your-username/project-aura.git)
    cd project-aura
    ```
2.  **Create and activate a Python 3.11 virtual environment:**
    ```
    py -3.11 -m venv venv_py311
    .\venv_py311\Scripts\activate
    ```
3.  **Install all the required libraries using the `requirements.txt` file:**
    ```
    pip install -r requirements.txt
    ```

### **3. Running the Application**

With your virtual environment activated, simply run the main script:
```
python main.py
```
The application window should launch, and after a few seconds, you should see your webcam feed with the facial landmarks being tracked.