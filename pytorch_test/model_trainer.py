import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import models
from donnees import Dataset_Precalculé

def train_model(data_dir, batch_size=16, epochs=10, lr=1e-4, save_path="resnet18_music_without_jazz_fixed.pth"):
    dataset = Dataset_Precalculé(data_dir)
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    print(len(train_loader.dataset))
    with open(os.path.join(data_dir, "labels.json")) as f:
        genre_to_idx = json.load(f)
    num_classes = len(genre_to_idx)
    print("Mapping :", genre_to_idx)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}")
    model = models.resnet18(weights="IMAGENET1K_V1")
    for param in model.parameters():
        param.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=lr)
    i = 0
    for epoch in range(epochs):
        model.train()
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        i+=batch_size
        if i%32 == 0:
            print(f"{i} musiques aanlysées")
    torch.save(model.state_dict(), save_path)
    print(f"Modèle sauvegardé dans {save_path}")

train_model(r"D:\BDDTIPE\Spectrogram_Training")
