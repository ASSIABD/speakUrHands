FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies: Java 17, Python 3, OpenCV libs, X11/GTK runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk \
    wget \
    unzip \
    python3 \
    python3-pip \
    python3-opencv \
    libgl1-mesa-glx \
    libgtk-3-0 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxrandr2 \
    ffmpeg \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Symlink python to python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# Download and install JavaFX 17 Linux SDK
RUN wget https://download2.gluonhq.com/openjfx/17.0.2/openjfx-17.0.2_linux-x64_bin-sdk.zip \
    && unzip openjfx-17.0.2_linux-x64_bin-sdk.zip -d /opt/ \
    && rm openjfx-17.0.2_linux-x64_bin-sdk.zip

ENV JAVAFX_HOME=/opt/javafx-sdk-17.0.2
ENV PATH=$PATH:$JAVAFX_HOME/bin

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy packaged JAR, recognition script, and trained model
COPY Mini_Projet_Java/Mini_Projet_Java/Code_Source/SpeakUrHands.jar app.jar
COPY Mini_Projet_Java/Mini_Projet_Java/Code_Source/src/controllers/asl_recognition.py ./asl_recognition.py
COPY Mini_Projet_Java/Mini_Projet_Java/Code_Source/training/best_model.keras ./best_model.keras

ENV DISPLAY=:0

# Run the JavaFX application
CMD ["java", "--module-path", "/opt/javafx-sdk-17.0.2/lib", "--add-modules", "javafx.controls,javafx.fxml", "-jar", "app.jar"]