import torch
import os

class Dataset_Precalculé(torch.utils.data.Dataset):
    def __init__(self, data_dir):
        self.fichiers = []
        for root, _, fichier in os.walk(data_dir):
            for f in fichier:
                if f.endswith(".pt"):
                    self.fichiers.append(os.path.join(root, f))

    def __len__(self):
        return len(self.fichiers)

    def __getitem__(self, idx):
        data = torch.load(self.fichiers[idx])
        return data["features"], data["label"]
