:loop
@echo off
echo Starting bot...
echo bot by EagleEye
python bot_script.py >> log.txt 2>&1
echo Bot stopped. Restarting in 10 seconds...
timeout /t 10
goto loop
