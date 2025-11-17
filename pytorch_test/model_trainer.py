import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models


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



def train_model(data_dir, batch_size=16, epochs=10, lr=1e-4, save_path="resnet18_music.pth"):
    # Charger dataset
    dataset = PrecomputedDataset(data_dir)

    # Split train/val (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # Charger mapping des genres
    with open(os.path.join(data_dir, "labels.json")) as f:
        genre_to_idx = json.load(f)
    num_classes = len(genre_to_idx)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Training on {device}")

    # Charger ResNet18 pré-entraîné
    model = models.resnet18(weights="IMAGENET1K_V1")
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)

    # Optimiseur & loss
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Boucle d’entraînement
    for epoch in range(epochs):
        model.train()
        running_loss, running_corrects = 0.0, 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(outputs.argmax(1) == labels)

        epoch_loss = running_loss / train_size
        epoch_acc = running_corrects.double() / train_size

        # Validation
        model.eval()
        val_loss, val_corrects = 0.0, 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(outputs.argmax(1) == labels)

        val_loss /= val_size
        val_acc = val_corrects.double() / val_size

        print(f"Epoch {epoch+1}/{epochs} "
              f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")

    # Sauvegarde du modèle
    torch.save(model.state_dict(), save_path)
    print(f"✅ Modèle sauvegardé dans {save_path}")
train_model(r"D:\BDDTIPE\Spectrograms")