import matplotlib.pyplot as plt
import numpy as np

categories = ['Rock','HipHop', 'Classique', 'Jazz']

pytorch_model = [62.58, 60.88, 81.1, 22.97]
k_plus_proches = [67.2, 60.47, 69.52, 13.85]

x = np.arange(len(categories))

bar_width = 0.3

plt.bar(x - bar_width/2, pytorch_model, width=bar_width, label='Modèle Pytorch', color='skyblue')

plt.bar(x + bar_width/2, k_plus_proches, width=bar_width, label='k-plus proches voisins', color='lightcoral')

plt.xlabel('Genre musical')
plt.ylabel('Taux de réussite (%)')
plt.title('Taux de réponses correctes ')
# Pour afficher les noms des catégories sur les positions de l'axe des x.
plt.xticks(x, categories)
plt.legend()

plt.show()