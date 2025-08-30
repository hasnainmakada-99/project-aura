# Project AURA 🧿

### The Intelligent AI-Powered Gaming & Productivity Companion

**Project AURA** is an advanced desktop application for Windows that combines computer vision, emotion detection, and intelligent audio processing to enhance your gaming performance and productivity. Using your webcam, AURA analyzes your focus, emotional state, and behavior patterns to automatically optimize your environment in real-time.

![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 **Key Features**

### 🧠 **Advanced Emotion Detection**
- **Real-time Emotion Analysis**: Detects happiness, sadness, frustration, exhaustion, stress, and confusion
- **Facial Expression Recognition**: 68-point facial landmark analysis for accurate emotion detection
- **Behavioral Pattern Analysis**: Monitors typing rhythms, mouse movements, and head posture
- **Multi-Monitor Behavior Tracking**: Analyzes window switching and cursor patterns across displays
- **Intelligent Response System**: Automatically adjusts environment based on emotional state

### 🎮 **Gaming Companion Intelligence**
- **🛡️ Anti-Cheat Safe Mode**: 100% compatible with Vanguard, VAC, and other anti-cheat systems
- **Game-Specific Audio Profiles**: Optimized for Valorant, CS2, Apex Legends, and more
- **Focus-Based Audio Enhancement**: Enhances crucial game audio when you're concentrated
- **Gaming Fatigue Detection**: Recommends breaks and adjusts settings during extended sessions
- **Real-time Performance Optimization**: Adapts to your gaming state for competitive advantage

### 🎯 **Smart Focus Detection**
- **Hybrid AI Model**: Combines OpenCV and Dlib for precise focus measurement
- **Eye Aspect Ratio Analysis**: Tracks alertness and attention levels
- **Head Pose Estimation**: Monitors head position and movement patterns
- **Dynamic Sensitivity**: Adjustable thresholds for different lighting and webcam conditions
- **Multi-Monitor Support**: Works seamlessly with multiple display setups

### 🎵 **Intelligent Audio Management**
- **Automatic Audio Ducking**: Lowers distracting audio when focused
- **Frequency Enhancement**: Boosts important audio frequencies based on context
- **Emotion-Based Music**: Plays calming or energizing audio based on detected mood
- **Break Reminders**: Smart notifications based on fatigue detection
- **Volume Optimization**: Adjusts system volumes based on stress levels

---

## 🎭 **Emotion Detection Capabilities**

### **Detected Emotional States:**
- **😊 Happy** - Smile detection with Duchenne markers and positive behavioral indicators
- **😢 Sad** - Frown detection with brow analysis and eyelid drooping patterns
- **😤 Frustrated** - Brow furrowing, jaw tension, and erratic behavioral patterns
- **😴 Exhausted** - Drooping eyelids, slow blinking, and posture changes
- **😰 Stressed** - Micro-expressions, rapid movements, and high system activity
- **🎯 Focused** - Stable gaze, minimal head movement, and sustained attention
- **🤔 Confused** - Head tilting, cursor hesitation, and irregular patterns
- **🧠 Concentrated** - Deep focus state with optimal attention metrics

### **Intelligent Actions:**
- **🎶 Audio Adjustments**: Calming music for stress, energizing for fatigue
- **⏰ Break Suggestions**: Personalized break recommendations based on patterns
- **🎮 Gaming Optimizations**: Audio enhancements and distraction reduction
- **💙 Wellness Support**: Gentle interventions and positive reinforcement
- **🏠 Environment Control**: Lighting and notification management

---

## 🛠️ **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.11 | Core application logic |
| **UI Framework** | PyQt6 | Modern desktop interface |
| **Computer Vision** | OpenCV + Dlib | Facial landmark detection |
| **Audio Control** | pycaw | Windows audio management |
| **Emotion AI** | Custom ML Models | Facial expression analysis |
| **System Integration** | Windows APIs | System monitoring and control |

---

## 🚀 **Installation & Setup**

### **Prerequisites**
- **Windows 10/11** (64-bit)
- **Python 3.11** or higher
- **Webcam** (built-in or external)
- **Microsoft C++ Build Tools** ([Download](https://visualstudio.microsoft.com/visual-cpp-build-tools/))
- **CMake** ([Download](https://cmake.org/download/)) - Add to system PATH

### **Installation Steps**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/hasnainmakada-99/project-aura.git
   cd project-aura
   ```

2. **Create Virtual Environment**
   ```bash
   py -3.11 -m venv venv_py311
   .\venv_py311\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   python main.py
   ```

### **First-Time Setup**
1. **Camera Permission**: Allow camera access when prompted
2. **Calibration**: Use the sensitivity sliders to calibrate for your setup
3. **Gaming Mode**: Enable gaming focus mode for competitive advantage
4. **Multi-Monitor**: Check multi-monitor mode if using multiple displays

---

## 🎮 **Gaming Mode Features**

### **Supported Games**
- **Valorant** - Footstep enhancement, distraction reduction
- **CS2** - Audio clarity optimization, voice comm priority
- **Apex Legends** - Combat audio enhancement, positioning audio
- **General FPS** - Universal competitive gaming optimizations

### **Anti-Cheat Compatibility**
- ✅ **Riot Vanguard** (Valorant)
- ✅ **VAC** (Steam games)
- ✅ **EasyAntiCheat**
- ✅ **BattlEye**
- ✅ **All major anti-cheat systems**

### **Gaming Intelligence Features**
- **Tilt Detection**: Identifies frustration and suggests breaks
- **Flow State Recognition**: Maintains optimal conditions during peak performance
- **Fatigue Monitoring**: Prevents performance degradation from exhaustion
- **Audio Advantage**: Enhances crucial game sounds without detection

---

## 📊 **Usage Examples**

### **Productivity Mode**
```
😊 Happy detected → Maintains positive environment
😤 Frustrated → Plays calming audio, suggests micro-break
😴 Tired → Recommends longer break, adjusts screen brightness
🎯 Focused → Reduces distractions, optimizes audio
```

### **Gaming Mode**
```
🎮 Gaming session started → Activates competitive audio profile
😰 Stressed → Reduces non-essential notifications
🏆 Flow state → Maintains optimal conditions
😪 Fatigued → Suggests break to maintain performance
```

---

## 🔧 **Configuration**

### **Sensitivity Settings**
- **Eye Openness Threshold**: Adjust for fatigue detection sensitivity
- **Focus Sensitivity**: Higher = more sensitive to attention changes
- **Emotion Confidence**: Minimum confidence for emotion detection

### **Audio Settings**
- **Gaming Mode**: Enable competitive audio enhancements
- **Emotion Response**: Toggle automatic audio adjustments
- **Break Reminders**: Customize notification frequency

### **Advanced Settings**
- **Multi-Monitor Mode**: Enable for multiple display setups
- **Camera Selection**: Choose primary camera for detection
- **Data Privacy**: All processing is local, no data sent externally

---

## 🛡️ **Privacy & Security**

- **🔒 Local Processing**: All emotion detection happens on your device
- **🚫 No Data Collection**: No personal data is transmitted or stored
- **🛡️ Anti-Cheat Safe**: Completely undetectable by gaming anti-cheat systems
- **🔐 Secure**: No network connections required for core functionality

---

## 🤝 **Contributing**

We welcome contributions! Please read our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 **Links**

- **Repository**: [GitHub](https://github.com/hasnainmakada-99/project-aura)
- **Issues**: [Bug Reports](https://github.com/hasnainmakada-99/project-aura/issues)
- **Discussions**: [Community](https://github.com/hasnainmakada-99/project-aura/discussions)

---

## 🙏 **Acknowledgments**

- **OpenCV** team for computer vision capabilities
- **Dlib** for facial landmark detection
- **PyQt6** for the modern UI framework
- **Gaming community** for feedback and testing

---

**🚀 Ready to enhance your gaming and productivity with AI? Download Project AURA today!**