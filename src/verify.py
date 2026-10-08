"""Recompute all method means and replay all 28 predictions on the included case."""

if not __debug__:
    raise RuntimeError('Verification requires assertions: do not use -O, -OO or PYTHONOPTIMIZE')
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/fresh_endpoint_metrics.json').read_text(encoding='utf-8'))
rows=data['rows']; methods=data['summary']
checks=0
for name, windows in methods.items():
    for window, archived in windows.items():
        selected=[r['rmse_kN'] for r in rows if r['method']==name and r['window']==window]
        assert np.isclose(np.mean(selected),archived['mean_case_rmse_kN'],rtol=0,atol=1e-10)
        checks+=1
with np.load(ROOT/'data/example_case32.npz',allow_pickle=False) as c, np.load(ROOT/'data/example_case32_predictions.npz',allow_pickle=False) as predictions:
    mask=c['t']>=30
    replay=0
    for r in rows:
        if r['case'] != 32 or r['window'] != 'overall': continue
        delta=predictions[f"case32_{r['method']}"][mask]-c['tension'][mask]
        rmse=np.sqrt(np.mean(delta**2))/1000
        assert np.isclose(rmse,r['rmse_kN'],rtol=0,atol=1e-10)
        replay+=1
finite=methods['truncated_physics_rff']['overall']['mean_case_rmse_kN']
persistent=methods['persistent_physics_rff']['overall']['mean_case_rmse_kN']
pair=data['paired_memory_comparisons']['rff_overall']
assert pair['wins']==0 and pair['cases']==16
assert np.isclose(finite-persistent,pair['mean_gain_kN'],rtol=0,atol=1e-10)
assert replay==len(methods)==28
print(json.dumps(dict(status='PASS', method_window_means=checks, replayed_case32_methods=replay,
    finite_rmse_kN=finite,persistent_rmse_kN=persistent,persistent_wins=0,test_cases=16,
    scope='All 16-case means reconstructed from archived scalar metrics; full time-series replay is included for one case only.')))
