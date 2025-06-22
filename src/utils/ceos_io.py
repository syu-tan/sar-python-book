import os
import struct
from glob import glob
import gc

import numpy as np
import cv2
import scipy
from scipy.interpolate import interp1d
from numpy.polynomial.polynomial import polyval2d
import tifffile
from tqdm import tqdm

from osgeo import gdal, osr

# CONSTANT
EARTH_RADIUS_LONG = 6378137.0  # tide-free system
EARTH_RADIUS_SHORT = 6356752.3141
EARTH_ACPECT_RATIO = 298.257223563
E2 = 1 - (1 - 1 / EARTH_ACPECT_RATIO) ** 2

EPSG = 4326
EPSG_STR = f'EPSG:{EPSG}'
PRIJECTION_WKT = 'PROJCS["WGS 84 / UTM zone 33N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'


class ConstantALOS(object):
    
    # LEVEl 1.1
    # DBS
    
    LEVEL = '1.1'
    
    # basic constants
    SIGNAL_DATA = 720
    
    IMG_LINE_SIZE = 8
    IMG_CELL_SIZE = 8
    IMG_OBRBIT_BLOCK = SIGNAL_DATA + 44
    
    EPSIRON = 1e-2
    
    LED_SUMMARY_LAMBDA = 720 + 500
    LED_ORBIT_POSITION = 720 + 4096 + 140
    LED_ORBIT_TIME_INTERVAL = 720 + 4096 + 0 + 182
    LED_ORBIT_TIME_FIRST = 720 + 4096 + 160
    LED_ORBIT_XYZ = 720 + 4096 + 386
    LED_LOCATION_CENTER_TIME = 720 + 68
    LED_SUMMARY_DOPPLER_ORB_PIX = 720 + 1414
    LED_SUMMARY_DOPPLER_RNG_PIX = 720 + 1478
    LED_SUMMARY_DOPPLER_ORB_TIME = 720 + 1542
    LED_SUMMARY_DOPPLER_RNG_TIME = 720 + 1606
    LED_SUMMARY_PRF = 720 + 934
    LED_DOPPER_CENTRIOD = 720 + 1734
    
    IMG_PRF = 0
    
    POL_ORDER = ['HH', 'HV', 'VV', 'VH']
    
    def __init__(self, version:int=1):
        self.version = version
        
        if version == 1:
            self.IMG_PREFIX = 412
            # ALOS-1 PALSAR
            # https://www.eorc.jaxa.jp/ALOS/jp/alos/a1_calval_j.htm
            # I don't know precision value, please tell me
            self.CALIBLATION_FACTOR = 83.0
            self.CALIBLATION_A = 0.
            
            self.LED_LOCATION_BLOCK = 720 + 4096 + 4680 + 8192 + 9860 + 1620 + 0 + 1540000 + 4314000 + 345000 + 325000 + 325000 + 3072 + 511000 + 4370000 + 728000 + 15000 + 1024
        elif version == 2:
            self.IMG_PREFIX = 544
            
            # ALOS-2 PALSAR-2
            # https://www.eorc.jaxa.jp/ALOS/jp/alos-2/a2_calval_j.htm
            self.CALIBLATION_FACTOR = 83.0
            self.CALIBLATION_A = 32.0
            
            self.LED_LOCATION_BLOCK = 720 + 4096 + 1620 + 4680 + 16384 + 9860 + 325000 + 511000 + 3072 + 728000 + 1024
            
        elif version == 4:
            # coming soon
            self.IMG_PREFIX = 0
            # ALOS-4 PALSAR-3
            # https://www.eorc.jaxa.jp/ALOS/jp/alos-4/a4_calval_j.htm
            self.CALIBLATION_FACTOR = 0
            self.CALIBLATION_A = 0
        else:
            raise ValueError(
                f'Version must be 1 or 2, Support for ALOS4 planned. Got {version}'
                )


def transform_latlogalt_earthfixearthcenter_coordirate(lat, lon, alt, stack_axis=2):
    pos_earth_scale = np.divide(
        EARTH_RADIUS_LONG,
        np.sqrt(
            1 - E2 * np.square(np.sin(lat))
        ))

    pos_ecef_xyz = np.stack([
            (pos_earth_scale + alt) * np.cos(lat) * np.cos(lon),
            (pos_earth_scale + alt) * np.cos(lat) * np.sin(lon),
            (pos_earth_scale * (1 - E2) + alt) * np.sin(lat),
        ], axis=stack_axis)
    
    return pos_ecef_xyz


def transform_earthcenter_earthfixearthcenter_coordirate(pos_ecef_xyz):
    pos_ecef_xyz = np.array(pos_ecef_xyz)
    x = pos_ecef_xyz[..., 0]
    y = pos_ecef_xyz[..., 1]
    z = pos_ecef_xyz[..., 2]

    lon = np.arctan2(y, x)
    p = np.sqrt(x ** 2 + y ** 2)
    lat = np.arctan2(z, p)

    pos_earth_scale = np.divide(
        EARTH_RADIUS_LONG,
        np.sqrt(
            1 - E2 * np.sin(lat) * np.sin(lat)
        ))

    alt = p / np.cos(lat) - pos_earth_scale

    return lat, lon, alt
            
            
class ALOSPALSARData(object):
    """
    ALOS Seriese (1,2,4) PALSAR Data Reader
    """
    
    def __init__(self, path_root, version=1, orbit='A', num_polarimetory=1):
        self.version = version
        self.constant = ConstantALOS(version)
        
        self.orbit = orbit
        self.num_polarimetory = num_polarimetory
        
        self.path_root = path_root
        
        if self.version == 1:
            self.path_leader = glob(path_root + f'/LED-ALPSRP*{self.constant.LEVEL}__{orbit}')[0]
        elif self.version == 2:
            self.path_leader = glob(path_root + f'/LED-ALOS2*{self.constant.LEVEL}__{orbit}')[0]
        
        self.path_imgs = []
        for i, pol in enumerate(self.constant.POL_ORDER):
            if i == self.num_polarimetory:
                break
            
            if self.version == 1:
                _path = glob(path_root + f'/IMG-{pol}-ALPSRP*{self.constant.LEVEL}__{orbit}')[0]
            elif self.version == 2:
                _path = glob(path_root + f'/IMG-{pol}-ALOS2*{self.constant.LEVEL}__{orbit}')[0]
                
            if _path:
                self.path_imgs.append(_path)
        
        if self.version == 1:
            self.path_volume = glob(path_root + f'/VOL-ALPSRP*{self.constant.LEVEL}__{orbit}')[0]
            self.path_trailer = glob(path_root + f'/TRL-ALPSRP*{self.constant.LEVEL}__{orbit}')[0]
        elif self.version == 2:
            self.path_volume = glob(path_root + f'/VOL-ALOS2*{self.constant.LEVEL}__{orbit}')[0]
            self.path_trailer = glob(path_root + f'/TRL-ALOS2*{self.constant.LEVEL}__{orbit}')[0]            
        
        # Lambda: wave length
        with open(self.path_leader, 'r') as LED:
            LED.seek(self.constant.LED_SUMMARY_LAMBDA)
            self.wave_length = float(LED.read(16))

    def caliburate(self, iq, official=False):
        if official:
            sigma = np.log10(np.square(iq) + self.constant.EPSIRON) * 10
        else:
            # https://www.eorc.jaxa.jp/ALOS/jp/alos-2/pdf/product_format_description/PALSAR-2_xx_Format_CEOS_J_g.pdf
            # 仕様書の定義では、レベル 1.1 ：σ0 = 10*log<I^2+Q^2> + CF -32.0 となっているが、視認性のために振幅値を使用
            sigma = np.log10(iq + self.constant.EPSIRON) * 10
        return sigma + self.constant.CALIBLATION_FACTOR - self.constant.CALIBLATION_A
    
    def read_slc(self, to8bit=True, cache=True):
        
        imgs = []
        
        for _idx_img, PATH_DATA in enumerate(self.path_imgs):
            with open(PATH_DATA, 'rb') as IMG:

                IMG.seek(236)
                line = int(IMG.read(self.constant.IMG_LINE_SIZE))
                IMG.seek(248)
                cell = int(IMG.read(self.constant.IMG_CELL_SIZE))
                
                rec = int(self.constant.IMG_PREFIX + cell * 8)
                rq = int(rec / 4)
                IMG.seek(self.constant.SIGNAL_DATA)
                
                slc = np.zeros(line * rq, dtype=np.float32)
                
                for _nline in tqdm(range(1, line), total=line, desc='Reading Signal...', ncols=80):
                    # split processing to reduce PC memory
                    _slc = struct.unpack(
                        ">%s" % (rq) + "f",
                        IMG.read(rec))
                    _slc = np.array(_slc, dtype=np.float32)
                    slc[_nline * len(_slc):(_nline + 1) * len(_slc)] = _slc
                    ## TODO: CEOS読み込みの記事の並列高速読み込みの適用

            slc = slc.reshape(-1, rq)
            slc = slc[:, int(self.constant.IMG_PREFIX / 4):]
            slc = slc[:,::2] + 1j * slc[:, 1::2]

            slc[np.isnan(slc)] = 0
            
            sigma = self.caliburate(np.abs(slc))
            phase = np.angle(slc)
            
            # process 8bit -1 for visualize on QGIS
            if to8bit:
                sigma = 254 * (sigma - sigma.min()) / (sigma.max() - sigma.min())
                sigma = sigma.astype(np.uint8)
                sigma = np.clip(cv2.equalizeHist(sigma), 0, 254)
                sigma += 1  # 0 : is nodata
            
            slc = sigma * np.cos(phase) + sigma * np.sin(phase) * 1j
            
            if _idx_img == 0:
                # original size
                self.N_LINE, self.N_SAMPLE = slc.shape[:2]
            
            imgs.append(slc)
            
        if cache:
            self.imgs = imgs
        return imgs
    
    def read_location(self,):

        with open(self.path_leader, 'rb') as LED:
            
            LED.seek(self.constant.LED_LOCATION_BLOCK, 0)

            A = np.array([float(coef) for coef in str(LED.read(500).decode()).split()])[::-1]
            B = np.array([float(coef) for coef in str(LED.read(500).decode()).split()])[::-1]
            A = A.reshape(5, 5)
            B = B.reshape(5, 5)
            self.A = A
            self.B = B

            # original point
            P0 = float(LED.read(20))
            L0 = float(LED.read(20))
            
        position = (
                polyval2d(-P0, -L0, B), polyval2d(-P0, -L0, A),
                polyval2d(P0, L0, B), polyval2d(P0, L0, A),
                polyval2d(-P0, L0, B), polyval2d(-P0, L0, A),
                polyval2d(P0, -L0, B), polyval2d(P0, -L0, A),
            )
        
        self.LT_LON, self.LT_LAT = position[4], position[5]
        self.RT_LON, self.RT_LAT = position[2], position[3]
        self.LB_LON, self.LB_LAT = position[0], position[1]
        self.RB_LON, self.RB_LAT = position[6], position[7]
        
        return position
    
    def read_orbit(self, velocity=False,):
        
        PATH_IMG = self.path_imgs[0]
        PATH_LED = self.path_leader
        
        with open(PATH_IMG, 'rb') as IMG:
            
            IMG.seek(self.constant.IMG_OBRBIT_BLOCK)
            TIME_START_SEC = struct.unpack(">i", IMG.read(4))[0]
            TIME_START_MSEC = TIME_START_SEC / 1000
            
            IMG.seek(236)
            line = int(IMG.read(8))
            
        with open(PATH_LED, 'rb') as LED:
            
            LED.seek(self.constant.LED_ORBIT_POSITION)
            num_point_sample = int(LED.read(4))
            
            LED.seek(self.constant.LED_ORBIT_TIME_INTERVAL)
            TIME_INTERVAL = round(float(LED.read(22)))

            LED.seek(self.constant.LED_ORBIT_TIME_FIRST)
            TIME_FIRST = float(LED.read(22))
            
            LED.seek(self.constant.LED_LOCATION_CENTER_TIME)
            TIME_CENTER_STR = LED.read(32)
            
            TIME_CENTER_MSEC = float(TIME_CENTER_STR[8:10]) * (60 ** 2) + \
                            float(TIME_CENTER_STR[10:12]) * 60 + \
                            float(TIME_CENTER_STR[12:14]) + \
                            float(TIME_CENTER_STR[14:17]) * 1e-3

            TIME_END = TIME_START_MSEC + (TIME_CENTER_MSEC - TIME_START_MSEC) * 2
            
            LED.seek(self.constant.LED_ORBIT_XYZ)
            POSITION_XYZ, VELOCITY_XYZ = [], []
            for _ in range(num_point_sample):
                x = float(LED.read(22))
                y = float(LED.read(22))
                z = float(LED.read(22))
                POSITION_XYZ.append([x, y, z])
                x_v = float(LED.read(22))
                y_v = float(LED.read(22))
                z_v = float(LED.read(22))
                VELOCITY_XYZ.append([x_v, y_v, z_v])
                
            POSITION_XYZ = np.array(POSITION_XYZ)
            VELOCITY_XYZ = np.array(VELOCITY_XYZ)
        
        TIME_OBSERVATION = np.arange(TIME_START_MSEC, TIME_END, (TIME_END - TIME_START_MSEC) / line)
        TIME_ORBIT = np.arange(TIME_FIRST, TIME_FIRST + TIME_INTERVAL * num_point_sample, TIME_INTERVAL)
        
        X_ORBIT = interp1d(TIME_ORBIT, POSITION_XYZ[:, 0], kind='cubic')(TIME_OBSERVATION)
        Y_ORBIT = interp1d(TIME_ORBIT, POSITION_XYZ[:, 1], kind='cubic')(TIME_OBSERVATION)
        Z_ORBIT = interp1d(TIME_ORBIT, POSITION_XYZ[:, 2], kind='cubic')(TIME_OBSERVATION)
        
        XYZ_ORBIT = np.stack([X_ORBIT, Y_ORBIT, Z_ORBIT], axis=1)  # (sample, 3)
        
        if velocity:
            X_VELOCITY = interp1d(TIME_ORBIT, VELOCITY_XYZ[:, 0], kind='cubic')(TIME_OBSERVATION)
            Y_VELOCITY = interp1d(TIME_ORBIT, VELOCITY_XYZ[:, 1], kind='cubic')(TIME_OBSERVATION)
            Z_VELOCITY = interp1d(TIME_ORBIT, VELOCITY_XYZ[:, 2], kind='cubic')(TIME_OBSERVATION)
            
            XYZ_VELOCITY = np.stack([X_VELOCITY, Y_VELOCITY, Z_VELOCITY], axis=1)
            return XYZ_ORBIT, XYZ_VELOCITY, TIME_OBSERVATION
        else:
            
            return XYZ_ORBIT, TIME_OBSERVATION
    
    def read_geo_matrix(self,):
            
            PATH_LED = self.path_leader
            with open(PATH_LED, 'rb') as LED:
                
                LED.seek(self.constant.LED_LOCATION_BLOCK)
                A_GEO = [float(LED.read(20)) for _ in range(25)][::-1]
                B_GEO = [float(LED.read(20)) for _ in range(25)][::-1]
                
                C_S = float(LED.read(20))
                C_L = float(LED.read(20))
                
                A_GEO = np.array(A_GEO).reshape(5, 5)
                B_GEO = np.array(B_GEO).reshape(5, 5)
                
            # cache
            self.A_GEO = A_GEO
            self.B_GEO = B_GEO
            self.C_S = C_S
            self.C_L = C_L
            
            return (A_GEO, B_GEO, C_S, C_L)
        
    def read_pixel_matrix(self,):
            
            PATH_LED = self.path_leader
            with open(PATH_LED, 'rb') as LED:
                
                OFFSET_GEO_MATRIX = 20 * 25 * 2 + 20 * 2
                LED.seek(self.constant.LED_LOCATION_BLOCK + OFFSET_GEO_MATRIX)
                A_PIX = [float(LED.read(20)) for _ in range(25)][::-1]
                B_PIX = [float(LED.read(20)) for _ in range(25)][::-1]
                
                C_LAT = float(LED.read(20))
                C_LON = float(LED.read(20))
                
                A_PIX = np.array(A_PIX).reshape(5, 5)
                B_PIX = np.array(B_PIX).reshape(5, 5)
                
            # cache
            self.A_PIX = A_PIX
            self.B_PIX = B_PIX
            self.C_S = C_LAT
            self.C_L = C_LON
            
            return (A_PIX, B_PIX, C_LAT, C_LON)
    
    def read_xyz_raster(self, A_GEO, B_GEO, C_S, C_L, dem=0, bbox=False, PATH_OUT='output'):
        
        index_sample = np.stack([np.arange(self.N_SAMPLE, dtype=np.uint16) for _ in range(self.N_LINE)], axis=0)
        index_line = np.stack([np.arange(self.N_LINE, dtype=np.uint16) for _ in range(self.N_SAMPLE)], axis=1)
        
        lat = polyval2d(index_sample - C_S, index_line - C_L, A_GEO)
        lon = polyval2d(index_sample - C_S, index_line - C_L, B_GEO)

        if bbox:
            self.bbox = bbox
            
            lat = self.write_crop_geotif(bbox=bbox, img=lat,
                                         PATH_GEOTIF=os.path.join(PATH_OUT, 'lat.tif')
                                         )
            lon = self.write_crop_geotif(bbox=bbox, img=lon,
                                         PATH_GEOTIF=os.path.join(PATH_OUT, 'lon.tif')
                                         )
            H_CROP, W_CROP = lat.shape

            dem = cv2.resize(dem, (W_CROP, H_CROP), interpolation=1)
        elif isinstance(dem, int):
            dem = cv2.resize(dem, (self.N_SAMPLE, self.N_LINE), interpolation=1)
            
        xyz = transform_latlogalt_earthfixearthcenter_coordirate(lat * np.pi / 180, lon * np.pi / 180, dem)
        return xyz, (index_sample, index_line)

    def write_single_look_complex(self, PATH_GEOTIF_SLC:str, imgs, amplitude=True):
        
        if imgs is None:
            imgs = self.imgs
        if not isinstance(imgs, list):
            imgs = [imgs]

        for idx_img, _img in enumerate(imgs):
            self.write_geotiff(PATH_GEOTIF_SLC.replace('.tif', f'_{self.constant.POL_ORDER[idx_img]}.tif'),
                               img=_img,
                               ch_name=self.constant.POL_ORDER[idx_img],
                               gdal_type=gdal.GDT_CFloat32,
                               )

        if amplitude:
            for idx_img, _img in enumerate(imgs):
                PATH_GEOTIF_AMP = PATH_GEOTIF_SLC.replace('.tif', f'_{self.constant.POL_ORDER[idx_img]}_amp.tif')
                self.write_geotiff(PATH_GEOTIF_AMP,
                                img=np.abs(_img),
                                ch_name=self.constant.POL_ORDER[idx_img],
                                gdal_type=gdal.GDT_Float32,
                                )
    
    def write_geotiff(self, PATH_GEOTIF:str, img, ch_name='Band', gdal_type=gdal.GDT_Float32, CH=1):

        (H, W) = img.shape[:2]

        driver = gdal.GetDriverByName('GTiff')
        # https://naturalatlas.github.io/node-gdal/classes/Constants%20(GDT).html
        out_dataset = driver.Create(PATH_GEOTIF, W, H, CH, gdal_type)
            
        if self.orbit == 'A':
            img = np.flipud(img)
        
        out_band = out_dataset.GetRasterBand(CH)
        out_band.WriteArray(img)
        out_band.SetDescription(ch_name)
        
        gcp_list = [
            gdal.GCP(self.LT_LON, self.LT_LAT, 0, 0, 0),
            gdal.GCP(self.RT_LON, self.RT_LAT, 0, W, 0),
            gdal.GCP(self.RB_LON, self.RB_LAT, 0, W, H),
            gdal.GCP(self.LB_LON, self.LB_LAT, 0, 0, H),
            ]
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(EPSG)
        out_dataset.SetGCPs(gcp_list, srs.ExportToWkt())
        out_dataset = None
        
    def crop_single_look_complex(self,
                                 bbox,
                                 PATH_GEOTIF:str,
                                 amplitude=True,
                                 height=None, width=None,):
        
        self.remove_original_data_cache()
        PATH_OUTPUT_GEOTIF = PATH_GEOTIF.replace('.tif', '_crop.tif')
        img_crop = self.crop_geotiff(
            bbox,
            PATH_OUTPUT_GEOTIF=PATH_OUTPUT_GEOTIF,
            PATH_INPUT_GEOTIF=PATH_GEOTIF,
            height=height, width=width,
        )
        
        if amplitude:
            PATH_GEOTIF_AMP = PATH_GEOTIF.replace('.tif', '_amp.tif')
            PATH_OUTPUT_GEOTIF_AMP = PATH_OUTPUT_GEOTIF.replace('.tif', '_amp.tif')
            self.crop_geotiff(
                bbox,
                PATH_OUTPUT_GEOTIF=PATH_OUTPUT_GEOTIF_AMP,
                PATH_INPUT_GEOTIF=PATH_GEOTIF_AMP,
                height=height, width=width,
            )
            
        return img_crop
    
    def write_crop_geotif(self, PATH_GEOTIF,
                          bbox=None, img=None,
                          height=None, width=None,):
        
        self.write_geotiff(PATH_GEOTIF=PATH_GEOTIF, img=img)
        
        PATH_GEOTIF_CROP = PATH_GEOTIF.replace('.tif', '_crop.tif')
        img_crop = self.crop_geotiff(
            bbox,
            PATH_GEOTIF_CROP,
            PATH_GEOTIF,
            height=height, width=width,)
        return img_crop
        
    def crop_geotiff(self,
                     bbox,
                     PATH_OUTPUT_GEOTIF:str,
                     PATH_INPUT_GEOTIF:str,
                     remove_input_file=False,
                     height=None, width=None,
                     nosave=False,
                     ):
        
        self.bbox = bbox
        
        if height and width:
            options = gdal.WarpOptions(
                format='GTiff',
                outputBounds=bbox,
                dstSRS=EPSG_STR,
                height=height, width=width,
                
                )
        else:
            # gdal translate crop
            options = gdal.WarpOptions(format='GTiff', outputBounds=bbox, dstSRS=EPSG_STR)
        
        gdal.Warp(
            srcDSOrSrcDSTab=PATH_INPUT_GEOTIF,
            destNameOrDestDS=PATH_OUTPUT_GEOTIF,
            options=options)
        
        if remove_input_file and os.path.exists(PATH_INPUT_GEOTIF):
            os.remove(PATH_INPUT_GEOTIF)

        imgs = tifffile.imread(PATH_OUTPUT_GEOTIF)
        
        if nosave:
            self.crop_imgs = imgs
        return imgs

    def remove_original_data_cache(self,):
        self.imgs = None
        gc.collect()

    def resize_crop_area(self, img):

        H, W = self.crop_imgs.shape[:2]
        img_resize = cv2.resize(img, (W, H), interpolation=1)
        return img_resize
    
    def read_doppler_coefficient(self,):
        with open(self.path_leader, 'rb') as LED:
            LED.seek(self.constant.LED_SUMMARY_DOPPLER_ORB_PIX)
            ORB_PIX_DOPPLER_COEF = [float(LED.read(16)) for _ in range(3)][::-1]
            ORB_PIX_DOPPLER_COEF = np.array(ORB_PIX_DOPPLER_COEF)
            
            LED.seek(self.constant.LED_SUMMARY_DOPPLER_RNG_PIX)
            RNG_PIX_DOPPLER_COEF = [float(LED.read(16)) for _ in range(3)][::-1]
            RNG_PIX_DOPPLER_COEF = np.array(RNG_PIX_DOPPLER_COEF)
            
            LED.seek(self.constant.LED_SUMMARY_DOPPLER_ORB_TIME)
            ORB_TIME_DOPPLER_COEF = [float(LED.read(16)) for _ in range(3)][::-1]
            ORB_TIME_DOPPLER_COEF = np.array(ORB_TIME_DOPPLER_COEF)
            
            LED.seek(self.constant.LED_SUMMARY_DOPPLER_RNG_TIME)
            RNG_TIME_DOPPLER_COEF = [float(LED.read(16)) for _ in range(3)][::-1]
            RNG_TIME_DOPPLER_COEF = np.array(RNG_TIME_DOPPLER_COEF)
            
        return ORB_PIX_DOPPLER_COEF, RNG_PIX_DOPPLER_COEF, ORB_TIME_DOPPLER_COEF, RNG_TIME_DOPPLER_COEF
    
    def read_doppler_centroid(self,):
        with open(self.path_leader, 'rb') as LED:
            LED.seek(self.constant.LED_DOPPER_CENTRIOD)
            DOPPLER_CENTROID_COEF = [float(LED.read(16)) for _ in range(2)][::-1]
            DOPPLER_CENTROID_COEF = np.array(DOPPLER_CENTROID_COEF)
            
        return DOPPLER_CENTROID_COEF
    
    def read_pulse_repetation_frequency(self,):
        """ Read Value PRF(pulse repetation frequency) [Hz] """
        with open(self.path_leader, 'rb') as LED:
            LED.seek(self.constant.LED_SUMMARY_PRF)
            prf = float(LED.read(16))
        return prf * 1e-3
    
