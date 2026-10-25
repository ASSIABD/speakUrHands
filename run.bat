@echo off
cd /d "%~dp0Mini_Projet_Java\Mini_Projet_Java\Code_Source"
echo ========================================================
echo Starting Speak Your Hands (JavaFX + Python ASL)...
echo ========================================================
java --module-path "C:\Users\HP\Desktop\cp\java tools\javafx-sdk-17.0.15\lib" --add-modules javafx.controls,javafx.fxml -cp "bin;C:\Users\HP\Desktop\cp\java tools\jfoenix-9.0.10.jar" application.Main
pause
