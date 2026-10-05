@echo off
chcp 65001 > nul
python ../src/main.py ../src/vfs.json "admin:$" script3.txt
pause