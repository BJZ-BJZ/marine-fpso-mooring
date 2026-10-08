"""Generate research figures from real project data. One figures/ dir per repo."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    'figure.dpi': 160, 'savefig.dpi': 160,
    'font.size': 10, 'axes.titlesize': 12, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9, 'legend.fontsize': 9,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.alpha': 0.3,
})
PALETTE = ['#1f6f9f', '#d96c2c', '#3a9e6e', '#8e5aa8', '#c0a02e', '#4aa3c7', '#e07b7b', '#6e7f80']

REPOS = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(7)


def savefig(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print('wrote', path)


def fpso_figs(d):
    m = json.load(open(d / 'data/causal_endpoint_metrics.json'))
    rows = pd.DataFrame(m['rows'])
    order_setting = ['clean', '1cm', '5cm']
    methods = {'noise_truncated_w41': 'Truncated memory', 'noise_persistent_w41': 'Persistent memory'}
    # fig1: RMSE by setting x method
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    x = np.arange(len(order_setting)); w = 0.35
    for i, (mk, label) in enumerate(methods.items()):
        means, stds = [], []
        for s in order_setting:
            v = rows[(rows['setting'] == s) & (rows['method'] == mk)]['rmse_kN']
            means.append(v.mean()); stds.append(v.std())
        ax.bar(x + (i - 0.5) * w, means, w, yerr=stds, capsize=4,
               color=PALETTE[i], label=label, edgecolor='k', lw=0.5)
    ax.set_xticks(x); ax.set_xticklabels(['Clean', '1 cm noise', '5 cm noise'])
    ax.set_ylabel('Endpoint RMSE (kN, mean ± SD over cases)')
    ax.set_title('FPSO mooring endpoint load error by noise setting')
    ax.legend()
    savefig(fig, d / 'figures/fig1_rmse_by_noise_setting.png')
    # fig2: case32 time series, line 0
    actual = np.load(d / 'data/example_case32.npz')
    pred = np.load(d / 'data/example_case32_predictions.npz')
    t = actual['t'][::5]
    # native arrays are in N; report in kN like the project metrics
    y = actual['tension'][::5, 0] / 1000.0
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(t, y, color='k', lw=1.2, label='Measured (line 1)')
    ax.plot(t, pred['case32_truncated_physics_rff'][::5, 0] / 1000.0, color=PALETTE[0], lw=1,
            label='Truncated-physics RFF')
    ax.plot(t, pred['case32_persistent_physics_rff'][::5, 0] / 1000.0, color=PALETTE[1], lw=1,
            label='Persistent-physics RFF')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Tension (kN)')
    ax.set_title('Case 32: measured vs predicted mooring tension (line 1)')
    ax.legend(loc='upper right')
    savefig(fig, d / 'figures/fig2_case32_tension_timeseries.png')



if __name__ == '__main__':
    d = REPOS
    (d / 'figures').mkdir(exist_ok=True)
    fpso_figs(d)
    print('done')
