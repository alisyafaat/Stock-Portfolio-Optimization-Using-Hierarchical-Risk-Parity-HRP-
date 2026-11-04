import numpy as np
import pandas as pd
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import riskfolio as rp
from scipy.cluster.hierarchy import leaves_list
from scipy.cluster.hierarchy import fcluster

warnings.filterwarnings("ignore")

# BACA DATA
price = pd.read_excel(
    r"C:\\Users\\syafa\\Downloads\\LSTM3.xlsx",
    decimal=","
)

price['Date'] = pd.to_datetime(price['Date'])
price.set_index('Date', inplace=True)

price = price.apply(pd.to_numeric, errors='coerce')

# RETURN
Y = np.log(price / price.shift(1)).dropna()

# KORELASI
corr = Y.corr()

# DENDROGRAM
plt.figure()
rp.plot_dendrogram(
    returns=Y,
    codependence='pearson',
    linkage='average',
    max_k=10,
    leaf_order=True
)

plt.title("Assets Dendrogram (Pearson & Average Linkage)")
plt.savefig(r"C:\\Users\\syafa\\Downloads\\dendrogramLSTMNEW.png", dpi=300)
plt.close()

# HRP
port = rp.HCPortfolio(returns=Y)

w = port.optimization(
    model='HRP',
    codependence='pearson',
    rm='MV',
    rf=0.06,
    linkage='average',
    max_k=10,
    leaf_order=True
)

#QUASI DIAGONALIZATION
Z = port.clustering
order_idx = leaves_list(Z)
order = Y.columns[order_idx]

corr_reordered = corr.loc[order, order]

#AMBIL CLUSTER
k = 3
clusters = fcluster(Z, k, criterion='maxclust')

# sesuaikan urutan dengan hasil reorder
clusters_ordered = clusters[order_idx]

#PLOT HEATMAP + KOTAK CLUSTER
plt.figure(figsize=(10, 8))

ax = sns.heatmap(
    corr_reordered,
    cmap='plasma',
    vmin=-1,
    vmax=1,
    center=0,
    square=True
)

# gambar kotak
start = 0
for i in range(1, len(clusters_ordered)):
    if clusters_ordered[i] != clusters_ordered[i-1]:
        ax.add_patch(plt.Rectangle((start, start), i-start, i-start,
                                   fill=False, edgecolor='magenta', lw=2))
        start = i

# kotak terakhir
ax.add_patch(plt.Rectangle((start, start), len(clusters_ordered)-start,
                           len(clusters_ordered)-start,
                           fill=False, edgecolor='magenta', lw=2))

plt.title("Quasi Diagonalization (HRP + Cluster Blocks)")
plt.savefig(r"C:\\Users\\syafa\\Downloads\\diagonalization_clusterLSTMNEW.png", dpi=300)
plt.show()

#BOBOT PORTOFOLIO
weights_df = w.copy()
weights_df.columns = ['Bobot_HRP']
weights_df = weights_df.reset_index()
weights_df.rename(columns={'index': 'Emiten'}, inplace=True)

# Ambil data
labels = weights_df['Emiten'].tolist()
sizes = weights_df['Bobot_HRP'].values

#PLOT PIE CLEAN
plt.figure(figsize=(8, 8))

colors = plt.cm.tab20.colors  

plt.pie(
    sizes,
    labels=None,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    textprops={'fontsize': 15}
)

plt.title("Bobot Portofolio HRP")

plt.legend(
    labels,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.15),
    ncol=4
)

plt.tight_layout()

plt.savefig(
    r"C:\\Users\\syafa\\Downloads\\bobot_portofolio_cleanLSTMNEW.png",
    dpi=300,
    bbox_inches='tight'
)

plt.show()

#KONTRIBUSI RISIKO
cov = Y.cov()

plt.figure()
rp.plot_risk_con(
    w=w,
    cov=cov,
    returns=Y,
    rm='MV',
    rf=0,
    alpha=0.05,
    height=6,
    width=10,
    t_factor=252
)

plt.title("Kontribusi Risiko Aset")
plt.savefig(r"C:\\Users\\syafa\\Downloads\\risk_contributionLSTMNEW.png", dpi=300)
plt.close()

#SIMPAN KE EXCEL
output_path = r"C:\\Users\\syafa\\Downloads\\Hasil_HRPLSTMNEW.xlsx"

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    weights_df.to_excel(writer, sheet_name='Bobot_HRP', index=False)
    Y.to_excel(writer, sheet_name='Return_Mingguan')
    corr.to_excel(writer, sheet_name='Korelasi')
    cov.to_excel(writer, sheet_name='Covariance')
    corr_reordered.to_excel(writer, sheet_name='Korelasi_Diagonal')

print("\nSemua hasil berhasil disimpan di:")
print(output_path)