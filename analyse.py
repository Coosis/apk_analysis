from apk_extract import ApkExtract as ae
import os


def main():
    # Initialize the ApkExtract object
    apk_extract = ae()
    apk_extract.process()

if __name__ == "__main__":
    main()
