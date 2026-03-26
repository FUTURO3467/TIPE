import matplotlib.pyplot as plt
import numpy as np

categories = ['Rock', 'Classique', 'HipHop']

pytorch_model = [66.1, 76.88, 83.8]
k_plus_proches = [67.51, 69.93, 53.49]

x = np.arange(len(categories))

bar_width = 0.3

plt.bar(x - bar_width/2, pytorch_model, width=bar_width, label='Modèle Pytorch', color='skyblue')

plt.bar(x + bar_width/2, k_plus_proches, width=bar_width, label='k-plus proches voisins', color='lightcoral')

plt.xlabel('Genre musical')
plt.ylabel('Taux de réussite (%)')
plt.title('Taux de réponses correctes sans le Jazz')
# Pour afficher les noms des catégories sur les positions de l'axe des x.
plt.xticks(x, categories)
plt.legend()

plt.show()