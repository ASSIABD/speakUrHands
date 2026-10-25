@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Speak Your Hands (JavaFX + Python ASL)...
echo ========================================================
java --module-path "C:\Users\HP\Desktop\cp\java tools\javafx-sdk-17.0.15\lib" --add-modules javafx.controls,javafx.fxml -cp "bin;C:\Users\HP\Desktop\cp\java tools\jfoenix-9.0.10.jar" application.Main
pause
