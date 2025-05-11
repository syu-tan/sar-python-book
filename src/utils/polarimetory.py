import math

import cv2
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


from utils.interferogram import (
    to8bit,
    )

# constants
SQRT2 = np.sqrt(2)

def decomposition_covariance(hh, hv, vv, vh):
    
    assert hh.shape == hv.shape == vv.shape == vh.shape, 'Shape must be same'
    
    # allocate memory
    
    Cr = np.zeros((3, 3, *hh.shape), dtype=np.float32)
    Ci = np.zeros((3, 3, *hh.shape), dtype=np.float32)
    
    # components
    k1r, k1i, k3r, k3i = np.real(hh), np.imag(hh), np.real(vv), np.imag(vv)
    k2r = (np.real(hv) + np.real(vh)) / SQRT2
    k2i = (np.imag(hv) + np.imag(vh)) / SQRT2

    # diagonal
    Cr[0][0] = k1r * k1r + k1i * k1i
    Cr[1][1] = k2r * k2r + k2i * k2i
    Cr[2][2] = k3r * k3r + k3i * k3i
    
    # off-diagonal
    Cr[0][1] = k1r * k2r + k1i * k2i
    Ci[0][1] = k1i * k2r - k1r * k2i
    Cr[0][2] = k1r * k3r + k1i * k3i
    Ci[0][2] = k1i * k3r - k1r * k3i
    Cr[1][2] = k2r * k3r + k2i * k3i
    Ci[1][2] = k2i * k3r - k2r * k3i

    # symmetry
    Cr[1][0], Ci[1][0] = Cr[0][1], -Ci[0][1]
    Cr[2][0], Ci[2][0] = Cr[0][2], -Ci[0][2]
    Cr[2][1], Ci[2][1] = Cr[1][2], -Ci[1][2]
    
    # ratio = 10 * np.log10(Cr[2][2] / Cr[0][0])
    # print(f'Ratio: {ratio}')
    
    C = Cr + Ci * 1j
    return C

def decomposition_coherency(hh, hv, vv, vh):
    
    assert hh.shape == hv.shape == vv.shape == vh.shape, 'Shape must be same'
    
    # allocate memory
    Tr = np.zeros((3, 3, *hh.shape), dtype=np.float32)
    Ti = np.zeros((3, 3, *hh.shape), dtype=np.float32)
    
    # components
    k1r = (np.real(hh) + np.real(vv)) / SQRT2
    k1i = (np.imag(hh) + np.imag(vv)) / SQRT2
    k2r = (np.real(hh) - np.real(vv)) / SQRT2
    k2i = (np.imag(hh) - np.imag(vv)) / SQRT2
    k3r = (np.real(hv) + np.real(vh)) / SQRT2
    k3i = (np.imag(hv) + np.imag(vh)) / SQRT2

    # diagonal
    Tr[0][0] = k1r * k1r + k1i * k1i
    Ti[0][0] = 0.0
    Tr[1][1] = k2r * k2r + k2i * k2i
    Ti[1][1] = 0.0
    Tr[2][2] = k3r * k3r + k3i * k3i
    Ti[2][2] = 0.0

    # off-diagonal
    Tr[0][1] = k1r * k2r + k1i * k2i
    Ti[0][1] = k1i * k2r - k1r * k2i
    Tr[0][2] = k1r * k3r + k1i * k3i
    Ti[0][2] = k1i * k3r - k1r * k3i
    Tr[1][2] = k2r * k3r + k2i * k3i
    Ti[1][2] = k2i * k3r - k2r * k3i

    # symmetry
    Tr[1][0], Ti[1][0] = Tr[0][1], -Ti[0][1]
    Tr[2][0], Ti[2][0] = Tr[0][2], -Ti[0][2]
    Tr[2][1], Ti[2][1] = Tr[1][2], -Ti[1][2]

    T = Ti + Ti * 1j
    return T

def decomposition_pauli(pol_basic, pol_cross, pol_like):

    
    # Pauli Decomposition
    single = (pol_basic + pol_like) / SQRT2
    double = (pol_basic - pol_like) / SQRT2
    volume  = pol_cross * SQRT2
    
    # RGB stack
    pauli = np.stack([double, volume, single], axis=2)
    return pauli

def normalize_intency_rgb(img):
    
    assert img.ndim == 3, 'Image must be 3D'
    
    for ch in range(img.shape[-1]):
        img[:,:,ch] = to8bit(img[:,:,ch], amp=True)
    img = img.astype(np.uint8)
    return img

def to_amp_clip_rgb(img, ch=3, a_min=4, a_max=12):
    if ch == 1:
        img = np.stack([img, img, img], axis=2)
    
    img = np.abs(img)
    img = np.log(img + 1e-1)
    img = np.clip(img, a_min, a_max)
        
    # normalize 8bit
    img = img - np.min(img)
    img = img / np.max(img)

    img = (img * 255).astype(np.uint8)
    return img

def decomposition_yamaguchi(covariance, coherency, 
                            weight=(1.0, 1.0, 1.0),
                            ):
    
    assert covariance.shape == coherency.shape, 'Shape must be same'
    
    # allocate memory
    Tr, Ti = np.real(coherency), np.imag(coherency)
    Cr, Ci = np.real(covariance), np.imag(covariance)
    ps = np.zeros_like(covariance[0][0])
    pd = np.zeros_like(covariance[0][0])
    pc = 2 * np.abs(coherency[1][2])
    sp = Tr[0][0] + Tr[1][1] + Tr[2][2]
    
    # weight
    k1, k2, k3 = weight
    
    # decomposition
    pv = (Tr[2][2] - 0.5 * pc) / k3
    s = Tr[0][0] - 0.5 * pv
    d = Tr[1][1] - k2 * pv - 0.5 * pc
    
    cR = Tr[0][1] - k1 * pv
    cI = Ti[0][1]
    c0 = Cr[0][2] - 0.5 * Cr[1][1] + 0.5 * pc

    ps[c0 < 0] = s[c0 < 0] - (cR * cR + cI * cI)[c0 < 0] / d[c0 < 0]
    pd[c0 < 0] = d[c0 < 0] + (cR * cR + cI * cI)[c0 < 0] / d[c0 < 0]
    ps[c0 > 0] = s[c0 > 0] + (cR * cR + cI * cI)[c0 > 0] / s[c0 > 0]
    pd[c0 > 0] = d[c0 > 0] - (cR * cR + cI * cI)[c0 > 0] / s[c0 > 0]

    # post processing
    condi = np.bitwise_and(ps > 0, pd < 0)
    pd[condi] = 0
    ps[condi] = sp[condi] - pv[condi] - pc[condi]
    condi = np.bitwise_and(ps < 0, pd > 0)
    ps[condi] = 0
    pd[condi] = sp[condi] - pv[condi] - pc[condi]
    condi = np.bitwise_and(ps < 0, pd < 0)
    ps[condi] = 0
    pd[condi] = 0
    pv[condi] = sp[condi] - pc[condi]

    yamaguchi = np.stack([pd, pv, ps], axis=2)
    return yamaguchi
