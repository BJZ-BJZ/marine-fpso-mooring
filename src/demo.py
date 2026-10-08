"""Causality and finite-versus-persistent memory on synthetic motion inputs."""
import json
import numpy as np
from physical_state import persistent_coordinates

n=240
v=np.zeros((n,9,3)); a=np.zeros_like(v)
v[:120,:,0]=.1
a[:120,:,2]=.02
d=dict(t=np.arange(n)*.1, velocity=v, acceleration=a)
finite=persistent_coordinates(d,0,None,80)
full=persistent_coordinates(d,0,None,None)
assert np.count_nonzero(finite[200:]) == 0
assert np.max(np.abs(full[200:])) > 0
later=dict(d, velocity=v.copy(), acceleration=a.copy())
later['velocity'][120:]+=5
assert np.array_equal(persistent_coordinates(later,0,None,None)[:120],full[:120])
assert np.array_equal(persistent_coordinates(later,0,None,80)[:120],finite[:120])
print(json.dumps(dict(status='PASS', input='Synthetic motion inputs and archived projected physical basis',
    finite_memory_zero_after_cutoff=True, persistent_memory_survives=True, future_invariance=True,
    scope='State mathematics only; this does not prove learned load accuracy or vessel safety.')))
