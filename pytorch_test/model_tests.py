import os
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import models
from donnees import Dataset_Precalculé
def test_model(data_dir, model_path, batch_size=16):
    dataset = Dataset_Precalculé(data_dir)
    test_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    with open(os.path.join(data_dir, "labels.json")) as f:
        genre_to_idx = json.load(f)

    idx_to_genre = {v: k for k, v in genre_to_idx.items()}
    num_classes = len(genre_to_idx)
    print("Mapping :", genre_to_idx)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(model_path))
    model = model.to(device)
    model.eval()
    stats = {}
    for genre in genre_to_idx:
        stats[genre + "_Test"] = 0
        stats[genre + "_Succes"] = 0
    confusion = [[0 for _ in range(num_classes)] for _ in range(num_classes)]
    nb_tests = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            labels.apply_(lambda a: 2 if a == 3 else a)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            for i in range(len(preds)):
                vrai = labels[i].item()
                pred = preds[i].item()
                vrai_name = idx_to_genre[vrai]
                pred_name = idx_to_genre[pred]
                stats[vrai_name + "_Test"] += 1
                stats[vrai_name + "_Succes"] += int(vrai == pred)
                confusion[vrai][pred] += 1
                nb_tests += 1
            if nb_tests %100 == 0:
                print(f"{nb_tests} musiques analysées")
    for genre in genre_to_idx:
        test = stats[genre + "_Test"]
        success = stats[genre + "_Succes"]
        stats[genre + "_Ratio"] = round(success / test, 4) if test > 0 else 0
    stats["Matrice_De_Confusion"] = confusion
    print("\n Résultats :")
    print(json.dumps(stats, indent=2))
    saveTestFile = "save_result.json"
    f = open(saveTestFile, 'w+')
    json.dump(stats, f, indent=1)
    f.close()
    print("\n Matrice de confusion (vrai en ligne, prédiction en colonne) :")
    for row in confusion:
        print(row)

    return stats, confusion

test_model(r"D:\BDDTIPE\Spectrogram_Tests", "resnet18_music_without_jazz_fixed.pth")
