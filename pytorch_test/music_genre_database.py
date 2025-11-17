import os
import torch
from torch.utils.data import Dataset
import torchaudio
import torchaudio.transforms as T
import torch.nn.functional as F

class MusicGenreDataset(Dataset):
    def __init__(self, data_dir, n_mels=128, fixed_len=5000, sample_rate=22050):
        """
        data_dir: dossier contenant un sous-dossier par genre avec les MP3
        n_mels: nombre de filtres Mel
        fixed_len: nombre de frames dans le spectrogramme final
        sample_rate: fréquence d'échantillonnage audio
        """
        self.data_dir = data_dir
        self.fixed_len = fixed_len
        self.sample_rate = sample_rate
        self.n_mels = n_mels

        self.files = []
        self.labels = []

        genres = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        self.genre_to_idx = {g: i for i, g in enumerate(genres)}

        for genre in genres:
            genre_path = os.path.join(data_dir, genre)
            for f in os.listdir(genre_path):
                if f.endswith(".mp3"):
                    self.files.append(os.path.join(genre_path, f))
                    self.labels.append(self.genre_to_idx[genre])

        # Transformation MelSpectrogram
        self.transform = T.MelSpectrogram(
            sample_rate=self.sample_rate,
            n_fft=2048,
            n_mels=self.n_mels
        )

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        # Charger audio
        audio, sr = torchaudio.load(self.files[idx])

        # Resample si nécessaire
        if sr != self.sample_rate:
            resample = T.Resample(sr, self.sample_rate)
            audio = resample(audio)
            sr = self.sample_rate

        # Convertir en mono si stéréo
        if audio.shape[0] > 1:
            audio = torch.mean(audio, dim=0, keepdim=True)

        # MelSpectrogram
        features = self.transform(audio)  # [1, n_mels, time]

        # Répéter sur 3 canaux pour ResNet18
        features = features.expand(3, -1, -1)  # [3, n_mels, time]

        # Padding ou cropping pour longueur fixe
        if features.shape[2] < self.fixed_len:
            pad_size = self.fixed_len - features.shape[2]
            features = F.pad(features, (0, pad_size))
        else:
            features = features[:, :, :self.fixed_len]

        label = self.labels[idx]
        return features, label