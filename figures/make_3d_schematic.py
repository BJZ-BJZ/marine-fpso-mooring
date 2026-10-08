"""3D schematic illustration for this project.
Rendered in Python (matplotlib) - not ANSYS/Fluent/STAR-CCM+ output.
Run: python make_3d_schematic.py  (needs matplotlib, numpy)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def hull_mesh(L=100.0, B=20.0, T=8.0, D=6.0, p=1.0, q=0.8, nx=61, ny=31):
    xs = np.linspace(-L/2, L/2, nx)
    a = np.linspace(0, np.pi, ny)
    X, A = np.meshgrid(xs, a)
    xn = 2*X/L
    hb = (B/2.0)*np.maximum(0.0, 1-xn**2)**p
    Y = hb*np.cos(A)
    Z = D - (D+T)*np.sin(A)**q
    return X, Y, Z

def draw_hull(ax, L, B, T, D, p=1.0, q=0.8, color='#b8c4cc', alpha=0.95):
    X, Y, Z = hull_mesh(L, B, T, D, p, q)
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, shade=True,
                    rstride=2, cstride=2, linewidth=0, antialiased=True)

def box(ax, x0,x1, y0,y1, z0,z1, color='lightgray', alpha=1.0):
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
                  [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    faces = [[v[0],v[1],v[2],v[3]],[v[4],v[5],v[6],v[7]],
             [v[0],v[1],v[5],v[4]],[v[2],v[3],v[7],v[6]],
             [v[1],v[2],v[6],v[5]],[v[4],v[7],v[3],v[0]]]
    ax.add_collection3d(Poly3DCollection(faces, facecolor=color, alpha=alpha,
                                        edgecolor='#333333', linewidths=0.4))

def plane(ax, x0,x1, y0,y1, z, color, alpha):
    X, Y = np.meshgrid([x0,x1],[y0,y1])
    ax.plot_surface(X, Y, np.full_like(X,float(z)), color=color, alpha=alpha, shade=False)

def water(ax, x0,x1, y0,y1, z=0):
    plane(ax, x0,x1, y0,y1, z, '#7fb3d5', 0.16)

def seabed(ax, x0,x1, y0,y1, z, color='#d9c9a8'):
    plane(ax, x0,x1, y0,y1, z, color, 0.5)
    for gx in np.linspace(x0,x1,9):
        ax.plot([gx,gx],[y0,y1],[z,z], color='#b09a72', lw=0.4, alpha=0.6)
    for gy in np.linspace(y0,y1,7):
        ax.plot([x0,x1],[gy,gy],[z,z], color='#b09a72', lw=0.4, alpha=0.6)

def mooring_line(ax, p0, p1, n=60, **kw):
    s = np.linspace(0,1,n)
    x = p0[0]+(p1[0]-p0[0])*s
    y = p0[1]+(p1[1]-p0[1])*s
    z = p0[2]+(p1[2]-p0[2])*(s**1.6)
    ax.plot(x, y, z, **kw)

def finish(ax, fname, title, elev=18, azim=-58):
    ax.set_title(title, fontsize=12, pad=10)
    ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)')
    ax.set_zlabel('z (m)')
    ax.view_init(elev=elev, azim=azim)
    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()
    print('saved', fname)

from pathlib import Path
import numpy as np

L, B, T, D = 280.0, 50.0, 18.0, 12.0
DEPTH = 130.0
fig = plt.figure(figsize=(11, 7.5))
ax = fig.add_subplot(111, projection='3d')

draw_hull(ax, L, B, T, D, p=0.55, q=1.0)
# deck cap
box(ax, -L/2, L/2, -B/2*0.92, B/2*0.92, D-0.5, D+0.5, color='#8a949c', alpha=0.9)
# topside block (schematic)
box(ax, -40, 40, -14, 14, D, D+16, color='#c9d2d8', alpha=0.95)

water(ax, -420, 420, -320, 320)
seabed(ax, -420, 420, -320, 320, -DEPTH)

# 9 mooring lines: 3 bundles (bow / midship / stern) x 3 lines fanning out
bundles = [110.0, 0.0, -110.0]
n = 0
for i, xb in enumerate(bundles):
    for j, ang in enumerate([-38, 0, 38]):
        side = 1 if (i + j) % 2 == 0 else -1
        rad = np.deg2rad(ang + (90 if side > 0 else -90))
        fair = (xb, side*(B/2)*0.98, -2.0)
        anch = (xb + 300*np.cos(rad)*0.9, side*300 + 300*np.sin(rad)*0.9, -DEPTH)
        mooring_line(ax, fair, anch, color='#1f4e79', lw=1.6)
        ax.scatter(*fair, s=22, c='#c0392b', depthshade=False)
        ax.scatter(*anch, s=14, c='#5d4037', depthshade=False)
        n += 1
print('lines:', n)
ax.text(0, 0, D+22, 'FPSO hull', fontsize=9, ha='center')
ax.text(300, 250, -DEPTH+4, 'seabed', fontsize=9)
ax.text(200, -260, -40, 'mooring line (x9)', fontsize=9, color='#1f4e79')
ax.text2D(0.02, 0.96, 'Innovation: physical memory states\nTruncated (finite) memory beats persistent memory\nat every window  -  w41: 3.14 vs 3.52 kN (-0.38 kN)',
    transform=ax.transAxes, fontsize=8.5, va='top', ha='left',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.88))
finish(ax, str(Path(__file__).parent / 'fig3_mooring_3d.png'),
       'FPSO nine-line mooring system - 3D schematic', elev=16, azim=-62)
