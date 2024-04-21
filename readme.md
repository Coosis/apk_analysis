# A project to analyse .apks to detect malware.
## dependencies:
```
pytorch
androguard
pyyaml
```

## To start, first clone the repository:
```bash
git clone https://github.com/Coosis/apk_analysis.git
```

### Windows:
Run win.bat to download the essentials. Verify download as the script suggests, and follow its instructions.

### Linux:
Run linux.sh to download the essentials. Verify download as the script suggests, and follow its instructions.

### MacOS:
Run mac.sh to download the essentials. Verify download as the script suggests, and follow its instructions.

# Steps:
1. Data Collection
Place the .apks in the `target` folder.
2. Data Preprocessing
Run the analyse.py script to extract the features from the .apks.
This will extract all .apks found and output to the `output` folder.
Extraction contains api calls and AndroidManifest.xml and more.
After extraction, the script use vocab.py to tokenize the api calls and save to model's `data` folder.
3. Model Training
Run the train.py script to train the model.
