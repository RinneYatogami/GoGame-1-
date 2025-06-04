pyinstaller startgame.py ^
--noconfirm ^
--onefile ^
--windowed ^
--add-data "game/Re2.wav;game" ^
--add-data "game/startwindow.jpg;game" ^
--add-data "game/Re.wav;game" ^
--add-data "lang/language.json;lang" ^
--icon=icongame.ico
