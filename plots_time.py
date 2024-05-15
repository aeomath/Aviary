import pandas as pd

import matplotlib.pyplot as plt

# Lire le fichier CSV
data = pd.read_csv("reports/aircraft_for_bench_FwFm/mission_timeseries_data.csv", sep=",")

# Afficher les premières lignes du fichier
print(data.head())
# Créer une figure avec une grille de sous-graphiques 4x3
fig, axs = plt.subplots(4, 3, figsize=(12, 12), sharex=True,sharey=False)
first_column = data.columns[0]
for i, column in enumerate(data.columns[1:]):
    row = i // 3
    col = i % 3
    axs[row, col].scatter(data[first_column], data[column], marker='.', color=plt.cm.tab10(i))
    axs[row, col].set_xlabel(first_column)
    axs[row, col].set_ylabel(column)
    axs[row, col].grid()
    
plt.tight_layout()
plt.subplots_adjust(hspace=0.5, wspace=0.3)
plt.show()

