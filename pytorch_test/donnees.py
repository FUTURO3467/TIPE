import torch
import os

class PrecomputedDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir):
        self.files = []
        for root, _, files in os.walk(data_dir):
            for f in files:
                if f.endswith(".pt"):
                    self.files.append(os.path.join(root, f))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        data = torch.load(self.files[idx])
        return data["features"], data["label"]