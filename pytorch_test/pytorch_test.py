from torch.utils.data import DataLoader
from music_genre_cnn import MusicGenreCNN
from music_genre_database import MusicGenreDataset
import torchvision.models as models
import torch.nn as nn
import torch
import torchaudio
import torchaudio.transforms as T

resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

transform = T.MelSpectrogram(
    sample_rate=22050,
    n_fft=2048,
    n_mels=128
)
# Adapter l’entrée (on garde 3 canaux → OK)
num_ftrs = resnet.fc.in_features
resnet.fc = nn.Linear(num_ftrs, 4)  # 4 genres

dataset = MusicGenreDataset(r"D:\BDDTIPE\Training\\", n_mels=128, fixed_len=5000)

train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
resnet = resnet.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(resnet.parameters(), lr=1e-4)

for epoch in range(10):
    resnet.train()
    for X, y in train_loader:
        X, y = X.to(device), y.to(device)

        optimizer.zero_grad()
        out = resnet(X)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()

    # Validation
    resnet.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for X, y in val_loader:
            X, y = X.to(device), y.to(device)
            preds = resnet(X).argmax(1)
            correct += (preds == y).sum().item()
            total += y.size(0)

    acc = correct / total
    print(f"Epoch {epoch+1}: Loss={loss.item():.4f}, ValAcc={acc:.2f}")


    def predict(model, filepath, transform, idx_to_genre):
        audio, sr = torchaudio.load(filepath)
        if sr != 22050:
            audio = T.Resample(sr, 22050)(audio)

        features = transform(audio).expand(3, -1, -1).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(features)
            pred = logits.argmax(1).item()
        return idx_to_genre[pred]


    idx_to_genre = {i: g for g, i in dataset.genre_to_idx.items()}
    print("CACA")
    print(predict(resnet, r"D:\BDDTIPE\Classical\Kai Engel - November.mp3", transform, idx_to_genre))