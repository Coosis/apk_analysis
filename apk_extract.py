import subprocess
import os
from androguard.misc import AnalyzeAPK

def disassemble_apk(apk_path):
    '''
    Disassemble APK file and extract AndroidManifest.xml using apktool.
    :param apk_path: Path to the APK file.
    :return: Androguard object containing the .dex files.
    '''
    # APK decoding using apktool
    root = os.path.dirname(os.path.abspath(__file__))
    tool_path = os.path.join(root, "target", "apktool")
    apk_name = os.path.basename(apk_path)
    output_path = os.path.join(root, "output", apk_name)

    apktool_command = f"{tool_path} d \"{apk_path}\" -o \"{output_path}\""
    # subprocess.run(apktool_command, shell=True)
    process = subprocess.Popen(apktool_command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.stdin.write('\n')
    process.stdin.flush()

    _, stderr = process.communicate()
    # error handling

    if process.returncode != 0:
        print(f"Error: {stderr}")
        return None

    # Extracting AndroidManifest.xml
    manifest_path = os.path.join(output_path, "AndroidManifest.xml")
    print(f"Extracted AndroidManifest.xml to: {manifest_path}")

    # Use Androguard to analyze .dex files
    _, _, dx = AnalyzeAPK(apk_path)

    return dx

def extract_api_calls(dx):
    '''
    Extract API calls from the .dex files.
    :param dx: Androguard object containing the .dex files.
    :return: List of API calls.
    '''
    api_calls = []
    for method in dx.get_external_methods():
        try:
            # getting rid of the semicolon
            class_name = method.class_name[:-1]
            method_name = method.name
            api_calls.append(class_name + "/" + method_name)
        except Exception as e:
            print(f"Error: {e}")

    return api_calls
