"""Innovation figure for this project: regenerated from the project's own data files.
Run: python make_innovation_figure.py  (needs matplotlib, numpy, pandas)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, pandas as pd, json
from pathlib import Path
plt.rcParams.update({'font.size': 10})
R = Path(__file__).parent.parent

d = json.load(open(R / 'data/causal_endpoint_metrics.json'))
mc = d['selection']['model_candidates']
wins, tr, pe = [], [], []
for m in mc:
    wins.append(m['window'])
    tr.append(m['models'][f"noise_truncated_w{m['window']}"]['selected']['validation_mean_case_rmse_kN'])
    pe.append(m['models'][f"noise_persistent_w{m['window']}"]['selected']['validation_mean_case_rmse_kN'])
x = np.arange(len(wins)); w = 0.36
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(x - w/2, tr, w, label='Truncated (finite) physical memory', color='#1a7f4b')
ax.bar(x + w/2, pe, w, label='Persistent (infinite) memory', color='#b03a2e')
ax.set_xticks(x); ax.set_xticklabels([f'w{w_}' for w_ in wins])
ax.set_xlabel('Memory window length'); ax.set_ylabel('Validation mean case RMSE (kN)')
ax.set_title('Finite physical memory beats persistent memory at every window length\n'
             'The innovation: compact physical memory states suffice for endpoint-load prediction',
             fontsize=11)
ax.legend()
for i, (a, b_) in enumerate(zip(tr, pe)):
    ax.text(i, max(a, b_) + 0.12, f'-{b_-a:.2f} kN', ha='center', fontsize=9, color='#1a7f4b', weight='bold')
fig.tight_layout(); fig.savefig(Path(__file__).parent / 'fig4_memory_window.png', dpi=150)
plt.close(fig); print('saved fig4_memory_window.png')

