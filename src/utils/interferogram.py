import math

import cv2
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from utils.ceos_io import transform_latlogalt_earthfixearthcenter_coordirate


def wrap_phase(src, scale=np.pi):
    # modulate phase to [-scale, scale]
    return (src + scale) % (2 * scale) - scale

def to8bit(img, amp=False):
    
    if amp:
        img = np.abs(img)
    img = img - np.min(img)
    img = img / np.max(img) * 255
    return img.astype(np.uint8)


def coregistration_phase_only_correlation(
        clx_m, clx_s,
        s_left_pad=0, s_right_pad=0, s_top_pad=0, s_bottom_pad=0,
        s_left_cut=0, s_right_cut=0, s_top_cut=0, s_bottom_cut=0
        ):

    H_A, W_A = clx_m.shape[:2]
    
    # cutting
    clx_s = clx_s[s_top_cut:H_A-s_bottom_cut, s_left_cut:W_A-s_right_cut]
    
    # paddigment
    clx_s = np.pad(clx_s, ((s_top_pad, s_bottom_pad), (s_left_pad, s_right_pad)), 'constant', constant_values=0)
    
    sigma_m = np.abs(clx_m).astype(np.float64)
    sigma_s = np.abs(clx_s).astype(np.float64)
    phase_m = np.angle(clx_m)
    phase_s = np.angle(clx_s)
    
    # phase only correlation
    difference, _ = cv2.phaseCorrelate(sigma_m, sigma_m)
    H_D, W_D = difference

    if W_D < 0 and H_D >= 0:
        W_D_ROUND = round(W_D)-1
        H_D_ROUND = round(H_D)
        h_slice, w_slice = slice(H_D_ROUND, H_A), slice(0, W_D_ROUND+W_A)
    elif W_D < 0 and H_D < 0:
        W_D_ROUND = round(W_D)-1
        H_D_ROUND = round(H_D)-1
        h_slice, w_slice = slice(0, H_D_ROUND+H_A), slice(0, W_D_ROUND+W_A)
    elif W_D >= 0 and H_D < 0:
        W_D_ROUND = round(W_D)
        H_D_ROUND = round(H_D)-1
        h_slice, w_slice = slice(0, H_D_ROUND+H_A), slice(W_D_ROUND, W_A)
    elif W_D >= 0 and H_D >= 0:
        W_D_ROUND = round(W_D)
        H_D_ROUND = round(H_D)
        h_slice, w_slice = slice(H_D_ROUND, H_A), slice(W_D_ROUND, W_A)
        
    phase_m_cut = phase_m[h_slice, w_slice]
    phase_s_cut = phase_s[h_slice, w_slice]
    sigma_m_cut = sigma_m[h_slice, w_slice]
    sigma_s_cut = sigma_s[h_slice, w_slice]
    
    # resize
    sigma_s_cut = cv2.resize(sigma_s_cut, (W_A, H_A), interpolation=cv2.INTER_LINEAR)
    phase_s_cut = cv2.resize(phase_s_cut, (W_A, H_A), interpolation=cv2.INTER_LINEAR)
    
    clx_m = sigma_m_cut * np.exp(1j * phase_m_cut)
    clx_s = sigma_s_cut * np.exp(1j * phase_s_cut)
    return clx_m, clx_s, difference

def coregistoration_homograhpy(
        img_m, img_s,
        max_pts=500, 
        good_match_rate=0.6,
        ):
    
    img_m = to8bit(img_m)
    img_s = to8bit(img_s)
    
    orb = cv2.ORB_create(max_pts)
    kp_m, des_m = orb.detectAndCompute(img_m, None)
    kp_s, des_s = orb.detectAndCompute(img_s, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    matches = bf.match(des_m, des_s)
    matches = sorted(matches, key=lambda x: x.distance)
    matches_good = matches[:int(len(matches) * good_match_rate)]
    
    src_pts = np.float32([kp_m[m.queryIdx].pt for m in matches_good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_s[m.trainIdx].pt for m in matches_good]).reshape(-1, 1, 2)
    
    homograpy, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
    return homograpy, (kp_m, kp_s), matches_good

def coregistoration_homomorphpy_cfloat(clx_m, clx_s,
                                       max_pts=500, 
                                       good_match_rate=0.6,
                                       select_match=30,
                                       ):
    H, W = clx_m.shape[:2]
    
    amp_m, phs_m = np.abs(clx_m), np.angle(clx_m)
    amp_s, phs_s = np.abs(clx_s), np.angle(clx_s)

    homograpy, (kp_m, kp_s), matches = coregistoration_homograhpy(amp_m, amp_s, max_pts, good_match_rate)
    
    amp_dst_s = cv2.warpPerspective(amp_s, homograpy, (W, H))
    phs_dst_s = cv2.warpPerspective(phs_s, homograpy, (W, H))

    # clx_dst_s = (amp_dst_s * np.cos(phs_dst_s) + amp_dst_s * np.sin(phs_dst_s) * 1j).astype(np.complex64)
    clx_dst_s = amp_dst_s * np.exp(1j * phs_dst_s).astype(np.complex64)
    
    # for debug image
    img_matches = cv2.drawMatches(
        to8bit(amp_m), kp_m, to8bit(amp_s), kp_s, matches[:select_match], None, flags=4,
        )
    
    return clx_dst_s, img_matches


def coherence_cell(clx_m, clx_s, i, eps=1e-2):
    
    sum1, sum2, sum3 = 0.0, 0.0, 0.0
    for i in range(len(clx_m)):
        m = clx_m[i]
        s = clx_s[i]
        sum1 += m * np.conj(s)
        sum2 += np.abs(m) ** 2
        sum3 += np.abs(s) ** 2

    return np.abs(sum1).mean() / (np.sqrt(sum2 * sum3).mean() + eps)

def coherence_single_process(clx_m, clx_s, patch_size=2):
    
    assert clx_m.shape[0] == clx_s.shape[0] and clx_m.shape[1] == clx_s.shape[1], 'Input images have different sizes'
    
    coh = np.zeros_like(clx_m, dtype=np.float32)

    for i in tqdm(range(clx_m.shape[0]), desc='Computing coherence...', total=clx_m.shape[0], ncols=80):
        for j in range(clx_m.shape[1]):
            if i == 0 or i == clx_m.shape[0]-1 or j == 0 or j == clx_m.shape[1]-1:
                coh[i, j] = 0
                continue
            coh[i, j] = coherence_cell(
                clx_m[i-patch_size:i+patch_size, j-patch_size:j+patch_size], 
                clx_s[i-patch_size:i+patch_size, j-patch_size:j+patch_size],
                i,)
    return coh


def coherence_multi_process(clx_m, clx_s, patch_size=2, n_jobs=8):

    assert clx_m.shape[0] == clx_s.shape[0] and clx_m.shape[1] == clx_s.shape[1], 'Input images have different sizes'
    
    H_COH, W_COH = clx_m.shape

    def compute_corr_line(i, PATCH_SZIE=patch_size, H_COH=H_COH, W_COH=W_COH):
        """
        Single Process by Line Function
        """
        
        coh_pl = np.zeros((W_COH), dtype=np.float32)
        
        for j in range(W_COH):
            if i < PATCH_SZIE or i >= H_COH-PATCH_SZIE or j < PATCH_SZIE or j >= W_COH-PATCH_SZIE:
                coh_pl[j] = 0
                continue
            coh_pl[j] = coherence_cell(
                clx_m[i-PATCH_SZIE:i+PATCH_SZIE, j-PATCH_SZIE:j+PATCH_SZIE],
                clx_s[i-PATCH_SZIE:i+PATCH_SZIE, j-PATCH_SZIE:j+PATCH_SZIE],
                i,
                )
            
        return (i, coh_pl)

    list_coh = Parallel(n_jobs=n_jobs)([
        delayed(compute_corr_line)(i) for i in tqdm(range(H_COH), desc='Coherence job paralell...', total=H_COH)
        ])

    # sorted by line
    list_coh.sort(key=lambda x: x[0])
    coh = np.stack([x[1] for x in list_coh], axis=0)
    return coh

def interferogram(clx_m, clx_s):
    """ Interferogram function """
    return np.angle(clx_m * np.conj(clx_s))


def orbital_stripe(sr_m, sr_s, wave_length):
    """ Orbital Stripe Function """
    stripe = wrap_phase(np.divide(4*np.pi*(sr_s - sr_m), wave_length))
    return stripe

def get_slant_range(xyz_orbit, xyz_location, index_line):
    slant_range = np.linalg.norm(xyz_orbit[index_line,:] - xyz_location, axis=2, keepdims=True)
    return slant_range[:,:,0] # (H, W, 1) -> (H, W)

def get_angle_vectors(v1, v2, eps=1e-2):
    dot_product = np.sum(v1 * v2, axis=-1)

    norm_v1 = np.linalg.norm(v1, axis=2)
    norm_v2 = np.linalg.norm(v2, axis=2)
    
    cos_angle = dot_product / (norm_v1 * norm_v2 + eps)
    
    # over angle cut
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angle_rad = np.arccos(cos_angle)
    return angle_rad

def slide_dem(r1_h, dem):
    """ Slide DEM Function """
    assert r1_h.shape == dem.shape, 'Input data have different shape'
    
    dem_slide = np.zeros_like(dem, np.float32)
    for _idx_line, r1_range in enumerate(r1_h):
        r1_range = (r1_range - r1_range.min()) / (r1_range.max() - r1_range.min())
        f = interp1d(r1_range, dem[_idx_line], kind='nearest')
        dem_slide[_idx_line] = f(np.linspace(0, 1, len(r1_range)))
    return dem_slide

def get_topography(r1, r2, r1_h, r2_h, lam):
    return  -wrap_phase(np.divide(
        np.pi*np.square(4)*(r2-r1 - (r2_h-r1_h)), lam))
    
def _convolve2d(image, kernel):
    shape = (image.shape[0] - kernel.shape[0] + 1, image.shape[1] - kernel.shape[1] + 1) + kernel.shape
    strides = image.strides * 2
    strided_image = np.lib.stride_tricks.as_strided(image, shape, strides)
    return np.einsum('kl,ijkl->ij', kernel, strided_image)

def _pad_singlechannel_image(image, kernel_shape, boundary):
    return np.pad(image, ((int(kernel_shape[0] / 2),), (int(kernel_shape[1] / 2),)), boundary)

def convolve2d(image, kernel, boundary='edge'):
    # reference: https://qiita.com/aa_debdeb/items/e74eceb13ad8427b16c6
    pad_image = _pad_singlechannel_image(image, kernel.shape, boundary) if boundary is not None else image
    return _convolve2d(pad_image, kernel)

def create_averaging_kernel(size = (5, 5)):
    return np.full(size, 1 / (size[0] * size[1]))

def goldshtein_phase_filter(img, filter_kernel, alpha=0.5, patch_size=32):
    
    img_fft = np.fft.fft2(img)
    img_fft = np.fft.fftshift(img_fft)

    if alpha > 0:
        if img_fft.shape == (patch_size, patch_size):
            _img_fft = convolve2d(img_fft, np.conj(filter_kernel))

        amp = np.abs(_img_fft)
        amp **= alpha
        img_fft *= amp
        
    img_fft = np.fft.ifftshift(img_fft)
    img = np.fft.ifft2(img_fft)
    return img

def goldshtein_phase_filter_sliding_window(img, alpha=0.75, patch_size=32, step=1, filter_size = 3):
    
    assert 0 < alpha <= 1, 'alpha must be greater than 0'

    filter_kernel = create_averaging_kernel((filter_size, filter_size)).astype(np.complex64)
    
    H, W = img.shape[:2]
    
    y_indxes = H // round(step)
    x_indxes = W // round(step)
    
    H_F, W_F = (y_indxes) * (step) + (patch_size), (x_indxes) * step + patch_size
    
    img = np.pad(img, ((0, H_F - H), (0, W_F - W)), 'constant', constant_values=(0, 0))

    img_count = np.zeros((H_F, W_F), dtype=np.int32)
    img_filter = np.zeros((H_F, W_F), dtype=np.complex64) + 1e-5
    
    for y in tqdm(range(0, y_indxes), desc='Phase Filtering', ncols=80, total=y_indxes):
        for x in range(0, x_indxes):
            
            y_start = y * patch_size
            y_end = y_start + patch_size
            
            x_start = x * patch_size
            x_end = x_start + patch_size
            
            patch = img[y_start:y_end, x_start:x_end]
            
            if patch.shape != (patch_size, patch_size):
                continue
            
            # phase enhancement filter
            patch_ = goldshtein_phase_filter(
                img=patch, 
                filter_kernel=filter_kernel, alpha=alpha,
                patch_size=patch_size,
                )
            
            img_filter[y_start:y_end, x_start:x_end] += patch_
            img_count[y_start:y_end, x_start:x_end] += 1
    
    #  mean pyramide
    img_filter[:H, :W] /= (img_count[:H, :W] + 1e-2)
    
    return img_filter[:H, :W]

def get_incident_angle(xyz_elev_loc, orb, idx_line):
    
    orb_idx = orb[idx_line, :]
    sla = orb_idx - xyz_elev_loc
    incident_angle = get_angle_vectors(sla, xyz_elev_loc)
    return incident_angle


