"""Frozen three-mode state implementation; projected basis supplied separately."""
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[1] / "data"
STATE_ZETA = .02
STATE_COUNT = 3

def persistent_coordinates(data,j,static,horizon=None):
    """Three actual-line load-directed modes; None retains the full prefix.

    State=(modal lag, modal lag-rate/omega), with the equilibrium projection
    B/omega^2 obtained from the settled catenary stiffness and dry lumped mass.
    Exact ZOH advance uses the previous sample only.
    Finite support is obtained by subtracting the propagated outgoing prefix.
    """
    with np.load(OUT/'load_directed_projection.npz') as basis:
        omega_modes=basis[f'line{j}_omega'][:STATE_COUNT]
        B=basis[f'line{j}_forcing'][:STATE_COUNT]
    v=data['velocity'][:,j]@B.T/omega_modes**2
    a=data['acceleration'][:,j]@B.T/omega_modes**2
    columns=[]
    for axis,omega in enumerate(omega_modes):
        A=omega*np.array([[0.,1.],[-1.,-2*STATE_ZETA]])
        wd=omega*np.sqrt(1-STATE_ZETA**2)
        Phi=np.exp(-STATE_ZETA*omega*.1)*(np.cos(wd*.1)*np.eye(2)+np.sin(wd*.1)/wd*(A+STATE_ZETA*omega*np.eye(2)))
        Gamma=np.linalg.solve(A,(Phi-np.eye(2))@np.array([0.,1.]))
        forcing=-a[:,axis]/omega-2*STATE_ZETA*v[:,axis]
        states=np.zeros((len(forcing),2))
        for k in range(1,len(forcing)):states[k]=Phi@states[k-1]+Gamma*forcing[k-1]
        if horizon is not None:
            assert horizon==80
            transition=np.linalg.matrix_power(Phi,horizon)
            states[horizon:]-=states[:-horizon].copy()@transition.T
            # The mathematical finite convolution is exactly zero for a zero
            # forcing record. Remove subtraction roundoff in this known case.
            active=np.r_[0,np.cumsum(forcing!=0)]
            k=np.arange(len(forcing));empty=active[k]-active[np.maximum(k-horizon,0)]==0
            states[empty]=0.
        columns.append(states)
    return np.column_stack(columns)
