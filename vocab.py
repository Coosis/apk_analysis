import os
import json

class Vocab:
    def __init__(self):
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.bin_dir = os.path.join(self.root, "bin")
        self.vocab_path = os.path.join(self.bin_dir, "vocab.json")
        self.app_dir = os.path.join(self.root, "output")

        self.vocab = self.build_vocab()

    def build_vocab(self):
        if not os.path.exists(self.vocab_path):
            with open(self.vocab_path, 'w') as f:
                json.dump({}, f, indent=4)
            return {}
        
        vocab = {}
        with open(self.vocab_path, 'r') as f:
            vocab = json.load(f)
        return vocab

    def populate_vocab(self):
        for app in os.listdir(self.app_dir):
            with open(os.path.join(self.app_dir, app, "api_calls.txt"), 'r') as f:
                for line in f:
                    api = line.strip()
                    if api not in self.vocab:
                        self.vocab[api] = len(self.vocab)
        with open(os.path.join(self.root, "bin", "vocab.json"), 'w') as f:
            json.dump(self.vocab, f, indent=4)

    def tokenize(self, api):
        if api in self.vocab:
            return self.vocab[api]
        return -1

if __name__ == "__main__":
    pass
