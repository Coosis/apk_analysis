#!/bin/bash

apktool_url="https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
apktool_dest="./target/apktool"

echo "Downloading apktool..."
curl $apktool_url -o $apktool_dest
chmod +x $dest
echo "Done downloading apktool."

jar_url="https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar"
jar_dest="./target/apktool.jar"

echo "Downloading apktool.jar..."
curl $jar_url -o $jar_dest
echo "Done downloading apktool.jar."

echo "setup completed."
echo "Try running the following command:"
echo "./target/apktool -v"
echo "If you see the version number, then the setup is successful, and you can close this window."
echo "Otherwise, download the latest version of apktool from:"
echo "https://bitbucket.org/iBotPeaches/apktool/downloads/"
echo "Name the jar file apktool.jar and place/replace the jar file in ./target folder."

