# Speak Your Hands 🖐️

An interactive desktop application for real-time **American Sign Language (ASL)** gesture detection and translation, built with **JavaFX** and **Python (TensorFlow / OpenCV)**.

---

## ✨ Features

- **Real-Time ASL Detection**: Captures webcam video, recognizes signs, and translates letters in real time.
- **Center Guide Box**: Built-in visual alignment box ("Place Hand Here") for consistent framing and high accuracy.
- **Non-Blocking Background AI Loading**: The camera turns on instantly (< 1s) while TensorFlow initializes asynchronously in the background.
- **ASL Learning & Quiz Modules**: Includes study flashcards and interactive quizzes.
- **Cross-Platform Ready**: Run directly on Windows or via Docker on Linux.

---

## 🚀 Running the Project

### Option A: Quick Run on Windows (No Setup Required)

If Java and Python are installed on your machine:
1. Simply double-click **`run.bat`** in this directory.
2. The application will start immediately.

---

### Option B: Running with Docker (Linux)

You can build and run the application completely isolated inside Docker.

#### 1. Build the Docker Image
```bash
docker build -t speakurhands:latest .
```

#### 2. Run the Container with Camera & Display Access
```bash
# Allow local container to access X11 display
xhost +local:root

# Run the container with GUI and camera passed through
docker run --rm -it \
  --name speakurhands-app \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --privileged \
  --device /dev/video0:/dev/video0 \
  speakurhands:latest
```

> **Note for Windows Docker users**: Docker on Windows runs inside WSL2 and does not pass USB webcams to Linux containers by default without [USBIP-WIN](https://github.com/dorssel/usbipd-win). For Windows, running natively with **`run.bat`** is recommended.

---

### Option C: Running from Eclipse IDE

1. Import the project from `Mini_Projet_Java/Mini_Projet_Java/Code_Source`.
2. Add JavaFX SDK to the project build path.
3. In **Run Configurations** -> **Arguments** -> **VM arguments**, enter:
   ```text
   --module-path "<path-to-javafx-sdk>/lib" --add-modules javafx.controls,javafx.fxml
   ```
4. Add `jfoenix-9.0.10.jar` to the classpath.
5. Run `application.Main`.

---

## 🧠 Model & Architecture

- **Base Architecture**: MobileNetV2 (fine-tuned on 26 ASL alphabet signs: A-Z).
- **Communication Pipeline**: JavaFX executes the Python backend as a child process. Python streams 30 FPS JPEG frames (Base64-encoded) and prediction strings via standard I/O pipes.
- **Weights File**: `Mini_Projet_Java/Mini_Projet_Java/Code_Source/training/best_model.keras`.

---

## 🛠️ Requirements

- **Java**: OpenJDK 17 or 21
- **JavaFX**: JavaFX 17 or 21 SDK
- **Python**: 3.10 or 3.11 with:
  ```bash
  pip install -r requirements.txt
  ```
