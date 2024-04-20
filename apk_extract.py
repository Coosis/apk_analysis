import subprocess
import os
from androguard.misc import AnalyzeAPK

def disassemble_apk(apk_path):
    # APK decoding using apktool
    path = os.path.dirname(os.path.abspath(__file__))
    tool_path = os.path.join(path, "target", "apktool")
    apk_name = os.path.basename(apk_path)
    output_path = os.path.join(path, "target", "output", apk_name)

    apktool_command = f"{tool_path} d \"{apk_path}\" -o \"{output_path}\""
    subprocess.run(apktool_command, shell=True)

    # Extracting AndroidManifest.xml
    manifest_path = os.path.join("target", "AndroidManifest.xml")
    print(f"Extracted AndroidManifest.xml to: {manifest_path}")

    # # Use Androguard to analyze .dex files
    # a, d, dx = AnalyzeAPK(apk_path)
    #
    # # Example: Print all class names
    # for dex in d:
    #     for clazz in dex.get_classes():
    #         print(clazz.get_name())

