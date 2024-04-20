@echo off
set apktool_url="https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat"
set apktool_dest="./target/apktool.bat"

echo Downloading apktool...
curl -o "%apktool_dest%" "%apktool_url%"
echo Done downloading apktool.

set jar_url="https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar"
set jar_dest=".\target\apktool.jar"

echo Downloading apktool.jar...
curl -o "%jar_dest%" "%jar_url%"
echo Done downloading apktool.jar.

echo setup completed.

echo Try running the following command:
echo ./target/apktool -v
echo If you see the version number, then the setup is successful, and you can close this window.
echo Otherwise, download the latest version of apktool from:
echo https://bitbucket.org/iBotPeaches/apktool/downloads/
echo Name the jar file apktool.jar and place/replace the jar file in ./target folder.
pause
