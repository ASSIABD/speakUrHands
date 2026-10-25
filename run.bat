@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Speak Your Hands (JavaFX + Python ASL)...
echo ========================================================
REM Set your JavaFX path here or set JAVAFX_HOME environment variable
if "%JAVAFX_HOME%"=="" (
    set JAVAFX_PATH=C:\Users\HP\Desktop\cp\java tools\javafx-sdk-17.0.15\lib
    echo Using default JavaFX path: %JAVAFX_PATH%
) else (
    set JAVAFX_PATH=%JAVAFX_HOME%\lib
    echo Using JAVAFX_HOME: %JAVAFX_HOME%
)
java --module-path "%JAVAFX_PATH%" --add-modules javafx.controls,javafx.fxml -jar SpeakUrHands.jar
pause
