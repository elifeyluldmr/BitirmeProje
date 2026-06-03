import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

labels = ['Normal', 'Phishing']
counts = [110862, 110587]
colors = ['#a6e3a1', '#f38ba8']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

ax1.bar(labels, counts, color=colors, edgecolor='white', linewidth=1.5)
ax1.set_title('Sinif Dagilimi - Cubuk Grafik', fontsize=12)
ax1.set_ylabel('Ornek Sayisi')
ax1.set_ylim(0, 130000)
for i, v in enumerate(counts):
    ax1.text(i, v + 1000, f'{v:,}', ha='center', fontweight='bold', fontsize=11)

ax2.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%',
        startangle=90, textprops={'fontsize': 11})
ax2.set_title('Sinif Dagilimi - Pasta Grafik', fontsize=12)

plt.suptitle('Nihai Veri Seti Sinif Dagilimi (Toplam: 221,449 Ornek)',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('sinif_dagilimi.png', dpi=150, bbox_inches='tight')
print("Grafik kaydedildi: sinif_dagilimi.png")
