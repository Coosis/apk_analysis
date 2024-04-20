import apk_extract
import os

def find_apk_files():
    """
    Find all APK files in the .target directory.
    rval: list of APK file paths
    """
    root_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(root_path, "target")
    apk_match = ".apk"
    apk_files = []
    for root, _, files in os.walk(target_path):
        for file in files:
            if file.endswith(apk_match):
                # print(f"Found APK file: {file}")
                apk_files.append(os.path.join(root, file))

    return apk_files

def main():
    apk_files = find_apk_files()
    for apk_file in apk_files:
        apk_extract.disassemble_apk(apk_file)

if __name__ == "__main__":
    main()
