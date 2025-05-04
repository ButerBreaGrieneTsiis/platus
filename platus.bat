@ECHO OFF
CLS
ECHO             ,,                                    
ECHO `7MM"""Mq.`7MM           mm                       
ECHO   MM   `MM. MM           MM                       
ECHO   MM   ,M9  MM   ,6"Yb.mmMMmm `7MM  `7MM  ,pP"Ybd 
ECHO   MMmmdM9   MM  8)   MM  MM     MM    MM  8I   `" 
ECHO   MM        MM   ,pm9MM  MM     MM    MM  `YMMMa. 
ECHO   MM        MM  8M   MM  MM     MM    MM  L.   I8 
ECHO .JMML.    .JMML.`Moo9^Yo.`Mbmo  `Mbod"YML.M9mmmP' 
ECHO                                      versie 1.2.1
ECHO.
ECHO maak een keuze:
ECHO.
ECHO     [1] verwerken
ECHO     [2] weergave
ECHO     [3] rapporteren
ECHO.

set /p op=keuze: 
if "%op%"=="1" goto verwerken
if "%op%"=="2" goto weergave
if "%op%"=="3" goto rapporteren

:verwerken
.venv\Scripts\python.exe -m platus.gegevens
GOTO End

:weergave
.venv\Scripts\streamlit.exe run weergave.py
GOTO End

:rapporteren
.venv\Scripts\streamlit.exe run rapporteren.py
GOTO End

:End