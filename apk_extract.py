import subprocess
import os
from androguard.misc import AnalyzeAPK

class ApkExtract:
    def __init__(self):
        """
        Initialize the ApkExtract object.
        """
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.target_dir = os.path.join(self.root, "target")
        self.tool_path = os.path.join(self.target_dir, "apktool")
        self.output_dir = os.path.join(self.root, "output")

    def find_apk_files(self):
        """
        Find all APK files in the ./target directory.
        :return: List of APK file names.
        """
        apk_match = ".apk"
        apk_files = []
        for _, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(apk_match):
                    # print(f"Found APK file: {file}")
                    apk_files.append(file)

        return apk_files

    def process(self):
        """
        Process the APK files in the ./target directory.
        Output the results to the ./output directory.
        """
        apk_names = self.find_apk_files()
        for apk_name in apk_names:
            dx = self.disassemble_apk(apk_name)
            self.extract_api_calls(dx, apk_name)

    def disassemble_apk(self, apk_name):
        '''
        Disassemble APK file and extract AndroidManifest.xml using apktool.
        :param apk_path: Path to the APK file.
        :return: Androguard object containing the .dex files.
        '''
        # APK decoding using apktool
        apk_path = os.path.join(self.root, "target", apk_name)
        output_path = os.path.join(self.output_dir, apk_name)

        apktool_command = f"{self.tool_path} d \"{apk_path}\" -o \"{output_path}\""
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

    def extract_api_calls(self, dx, apk_name):
        '''
        Extract API calls from the .dex files.
        :param dx: Androguard object containing the .dex files.
        '''
        for method in dx.get_external_methods():
            try:
                # getting rid of the semicolon
                class_name = method.class_name[:-1]
                method_name = method.name
                with open(os.path.join(self.output_dir, apk_name, "api_calls.txt"), "a") as f:
                    f.write(f"{class_name}/{method_name}\n")
            except Exception as e:
                print(f"Error: {e}")
