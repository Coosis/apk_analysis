import apk_extract
import os

def find_apk_files():
    """
    Find all APK files in the ./target directory.
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
    root = os.path.dirname(os.path.abspath(__file__))
    for apk_file in apk_files:
        dx = apk_extract.disassemble_apk(apk_file)
        api_calls = apk_extract.extract_api_calls(dx)
        apk_name = os.path.basename(apk_file)
        api_calls_file = os.path.join(root, "output", apk_name, f"{apk_name}_api_calls.txt")
        print(f"Saving API calls in {api_calls_file}:")

        try:
            with open(f"{api_calls_file}", "a") as f:
                for api_call in api_calls:
                    f.write(f"{api_call}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
