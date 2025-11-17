import os
import json
import torch
import torchaudio
import torchaudio.transforms as T
import torch.nn.functional as F

# 📌 Paramètres
DATA_DIR = r"D:\BDDTIPE\Training"   # ton dataset avec sous-dossiers rock/, rap/, etc.
OUT_DIR = r"D:\BDDTIPE\Spectrograms"  # dossier où stocker les spectrogrammes
SAMPLE_RATE = 22050
N_MELS = 128
FIXED_LEN = 5000

os.makedirs(OUT_DIR, exist_ok=True)

# Genres = sous-dossiers
genres = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
genre_to_idx = {g: i for i, g in enumerate(genres)}

# Sauvegarde du mapping
with open(os.path.join(OUT_DIR, "labels.json"), "w") as f:
    json.dump(genre_to_idx, f)

# Transformation audio
mel_transform = T.MelSpectrogram(
    sample_rate=SAMPLE_RATE,
    n_fft=2048,
    n_mels=N_MELS
)

count = 0
for genre in genres:
    genre_path = os.path.join(DATA_DIR, genre)
    out_genre_path = os.path.join(OUT_DIR, genre)
    os.makedirs(out_genre_path, exist_ok=True)
    for f in os.listdir(genre_path):
        if not f.endswith(".mp3"):
            continue

        filepath = os.path.join(genre_path, f)

        try:
            # 1. Charger
            audio, sr = torchaudio.load(filepath)

            # 2. Resample
            if sr != SAMPLE_RATE:
                audio = T.Resample(sr, SAMPLE_RATE)(audio)

            # 3. Convertir en mono
            if audio.shape[0] > 1:
                audio = torch.mean(audio, dim=0, keepdim=True)

            # 4. Spectrogramme
            features = mel_transform(audio)  # [1, N_MELS, time]
            features = features.expand(3, -1, -1)  # [3, N_MELS, time]

            # 5. Padding / crop
            if features.shape[2] < FIXED_LEN:
                pad_size = FIXED_LEN - features.shape[2]
                features = F.pad(features, (0, pad_size))
            else:
                features = features[:, :, :FIXED_LEN]

            # 6. Sauvegarde tensor
            out_file = os.path.join(out_genre_path, f.replace(".mp3", ".pt"))
            torch.save({
                "features": features,
                "label": genre_to_idx[genre]
            }, out_file)

            count += 1
            if count % 100 == 0:
                print(f"{count} fichiers traités...")

        except Exception as e:
            print(f"⚠️ Erreur avec {filepath}: {e}")

print(f"✅ Terminé ! {count} spectrogrammes sauvegardés dans {OUT_DIR}")