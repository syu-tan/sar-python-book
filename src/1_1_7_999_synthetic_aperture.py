# ## `Synthetic Aperture Processing
# 
# ## 概要
# 
# ALOS PALSAR の合成開口処理の Python 実装例です。記事で公開した処理の再現を行えるコードです。
# 
# JAXA CEOS フォーマット仕様書: [CEOS JAXA](https://www.eorc.jaxa.jp/ALOS/jp/alos/fdata/PALSAR_L10idx_wingidx_wingPa.zip) Level 1.0
# 
# ## 使用データ
# 
# | 項目 | 情報 |
# | ---- | ---- | 
# | 衛星 | ALOS PALSAR |
# | 観測シーンID　| `ALPSRP051270700-L1.0`　東京湾の観測 |
# | データリンク | [ASF](https://search.asf.alaska.edu/#/?zoom=9.248&center=139.552,35.184&dataset=ALOS&resultsLoaded=true&granule=ALPSRP051270700-KMZ&searchType=List%20Search&searchList=ALPSRP051270700) Level 1.0 Image |
# | 画像クレジット| © JAXA |

# # 環境構築
# ## Environment
# 
# ## 動作環境
# - Python: 3.6++ 
# 
# ## 推奨環境
# - Python バージョン 3.10 以上
# - Recommendation: Version >= `3.10`
# 
# 以下のコマンドで環境構築が可能
# ```shell
# pip install numpy matplotlib tqdm scipy
# ```


import os, gc, warnings, struct, math, json, time
import numpy as np
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from tqdm import tqdm

PATH_OUTPUT = os.path.join('output', '1_1_1_999_synthetic_aperture')
os.makedirs(PATH_OUTPUT, exist_ok=True)


PATH_CEOS_FOLDER = os.path.join("..", "data", "raw", "ALPSRP051270700-L1.0") # To folder containing the CEOS data
PATH_CEOS_FOLDER = os.path.join("../../insar", "data", "raw", "ALPSRP051270700-L1.0") # To folder containing the CEOS data

PATH_CEOS_DIRNAME = os.path.basename(PATH_CEOS_FOLDER)
print(f'PALSAR SCENE ID: {PATH_CEOS_DIRNAME}')

POLARIMETORY = 'HH' # 'HH', 'HV', 'VV', 'VH'
ORBIT_NAME = 'A' # 'A', 'D': ascending or descending

PATH_CEOS_FILE_NAME_BASE = PATH_CEOS_DIRNAME.replace('-L1.0', '-H1.0')
PATH_IMG = os.path.join(PATH_CEOS_FOLDER, f'IMG-{POLARIMETORY}-{PATH_CEOS_FILE_NAME_BASE}__A')
PATH_LED = os.path.join(PATH_CEOS_FOLDER, f'LED-{PATH_CEOS_FILE_NAME_BASE}__A')

# check if the files exist
if not os.path.exists(PATH_IMG) or not os.path.exists(PATH_LED):
    print()
    raise FileNotFoundError(f'--->>> {PATH_IMG} or {PATH_LED} does not exist')


# ## Global Fix Value
TIME_DAY_HOUR   = 24
TIME_DAY_MINITE = 60
TIME_MINITE_SEC =  60
TIME_DAY_SEC = TIME_DAY_HOUR * TIME_DAY_MINITE * TIME_MINITE_SEC # sec
SOL = 299792458.0 # m/s speed of light

DIGIT4 = 1000.

BYTE1 = 1
BYTE2 = 2
INTERGER4 = 4
INTERGER6 = 6
FLOAT16 = 16
FLOAT22 = 22
FLOAT32 = 32
FLOAT64 = 64


# ## Read `IMG` File
# 
# JAXA CEOS フォーマットのバイナリー番地情報と格納値の意味を共に出力しています。


f = open(PATH_IMG, "rb")


# ### 表3.3-10 SARデータファイルディスクリプタレコード
f.seek(8)
NUM_SAR_DISCRIPTOR_RECORD = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 レコード長 = 720）10 ->', NUM_SAR_DISCRIPTOR_RECORD)

f.seek(276)
NUM_PREFIX = int(f.read(INTERGER4))
print('46 277 － 280 I4 レコードあたりのPREFIX DATAのバイト数 ＝ b412 ：固定 ->', NUM_PREFIX)
f.seek(180)
NUM_SIGNAL_RECORD = int(f.read(INTERGER6))
print('29 181 － 186 I6 SARデータレコード数 シグナルデータレコード数 ->', NUM_SIGNAL_RECORD)
f.seek(186)
signal_record_length = int(f.read(INTERGER6))

print(f'{"="*10} Header {NUM_PREFIX} {"="*10}')

f.seek(48 + NUM_SAR_DISCRIPTOR_RECORD)
pol = int.from_bytes(f.read(BYTE2), byteorder="big")
print('16 49 － 50 B2 SARチャンネルID = 1：1偏波、2：2偏波、4：ポラリメトリ ->', pol)
f.seek( 8 + NUM_SAR_DISCRIPTOR_RECORD)
record_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 レコード長（観測モード及びオフナディア角から求められるレコードサイズで、実際のレコード長） ->', record_length) 
f.seek(12 + NUM_SAR_DISCRIPTOR_RECORD)
azimuth_line = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('7 13 － 16 B4 SAR画像データライン番号 ＝ 1、2、3……・ ->', azimuth_line)
f.seek(16 + NUM_SAR_DISCRIPTOR_RECORD)
sar_image_index = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('8 17 － 20 B4 SAR画像データレコードインデックス ＝ 1：固定 (画像ライン内でのレコード順序番号) ->', sar_image_index)
f.seek(24 + NUM_SAR_DISCRIPTOR_RECORD)
NUM_PIXEL = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('10 25 － 28 B4 実際のデータピクセル数 ->', NUM_PIXEL)
f.seek(28 + NUM_SAR_DISCRIPTOR_RECORD)
NUM_BLANK_PIXEL = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('11 29 － 32 B4 実際の右詰めのピクセル数 ->', NUM_BLANK_PIXEL)
f.seek(56 + NUM_SAR_DISCRIPTOR_RECORD)
prf = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('20 57 － 60 B4 PRF [mHz] ->', prf)
f.seek(66 + NUM_SAR_DISCRIPTOR_RECORD)
chirp = int.from_bytes(f.read(BYTE2), byteorder="big")
print('23 67 － 68 B2 チャープ形式指定者 0=LINEAR FM CHIRP 1=PHASE MODULATORS ->', chirp)
f.seek(68 + NUM_SAR_DISCRIPTOR_RECORD)
chirp_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('24 69 － 72 B4 チャープ長(パルス幅) nsec （チャープ長さ） ->', chirp_length)
f.seek(72 + NUM_SAR_DISCRIPTOR_RECORD)
chirp_const = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('25 73 － 76 B4 チャープ定数係数 Hz ノミナル値 ->', chirp_const)
f.seek(76 + NUM_SAR_DISCRIPTOR_RECORD)
chirp_coeff = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('26 77 － 80 B4 チャープ一次係数 Hz/μsec ノミナル値 ->', chirp_coeff)
f.seek(80 + NUM_SAR_DISCRIPTOR_RECORD)
chirp_coeff2 = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('27 81 － 84 B4 チャープ二次係数 Hz/μsec2 ノミナル値 ->', chirp_coeff2)
f.seek(92 + NUM_SAR_DISCRIPTOR_RECORD)
gain = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('30 93 － 96 B4 受信機ゲイン dB ノミナル値 ->', gain)
f.seek(116 + NUM_SAR_DISCRIPTOR_RECORD)
DIS_NEAR_RANGE = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('36 117 － 120 B4 最初のデータまでのスラントレンジ [m] ->', DIS_NEAR_RANGE)



# ### 表3.3-11 シグナル・データ・レコード
f.seek( NUM_SAR_DISCRIPTOR_RECORD)
print('Num of Range: ', NUM_PIXEL, 'Num of Azimuth Line: ', NUM_SIGNAL_RECORD)

signal = np.zeros((NUM_SIGNAL_RECORD, NUM_PIXEL), dtype=np.complex64)

for i in tqdm(range(NUM_SIGNAL_RECORD)):
    if i == 0:
        print(f'{"="*10} Start Time {"="*10}');
        _ = f.read(36)
        TIME_OBS_START_YEAR = f.read(INTERGER4)
        TIME_OBS_START_YEAR = int.from_bytes(TIME_OBS_START_YEAR, 'big')
        print('13 37 － 40 B4 センサー取得年 ->', TIME_OBS_START_YEAR)
        TIME_OBS_START_DAY = f.read(INTERGER4)
        TIME_OBS_START_DAY = int.from_bytes(TIME_OBS_START_DAY, 'big')
        print('14 41 － 44 B4 センサー取得日（年内通算） ->', TIME_OBS_START_DAY)
        TIME_OBS_START_MSEC = f.read(INTERGER4)
        TIME_OBS_START_MSEC = int.from_bytes(TIME_OBS_START_MSEC, 'big')
        print('15 45 － 48 B4 センサー取得ミリ秒（日内通算） ->', TIME_OBS_START_MSEC)
        _ = f.read(NUM_PREFIX - (36 + 4 * 3))
        
    elif i == NUM_SIGNAL_RECORD - 1:
        
        print(f'{"="*10} End Time {"="*10}');
        _ = f.read(36)
        TIME_OBS_END_YEAR = f.read(INTERGER4)
        TIME_OBS_END_YEAR = int.from_bytes(TIME_OBS_END_YEAR, 'big')
        print('13 37 － 40 B4 センサー取得年 ->', TIME_OBS_END_YEAR)
        TIME_OBS_END_DAY = f.read(INTERGER4)
        TIME_OBS_END_DAY = int.from_bytes(TIME_OBS_END_DAY, 'big')
        print('14 41 － 44 B4 センサー取得日（年内通算） ->', TIME_OBS_END_DAY)
        TIME_OBS_END_MSEC = f.read(INTERGER4)
        TIME_OBS_END_MSEC = int.from_bytes(TIME_OBS_END_MSEC, 'big')
        print('15 45 － 48 B4 センサー取得ミリ秒（日内通算） ->', TIME_OBS_END_MSEC)
        _ = f.read(NUM_PREFIX - (36 + 4 * 3))
        
    else:
        _ = f.read(NUM_PREFIX)
    
    if i >= NUM_SIGNAL_RECORD - 2:
        # single processing
        for j in range(NUM_PIXEL):
            byte_hh_r = f.read(BYTE1)
            byte_hh_i = f.read(BYTE1)
            hh_real = int.from_bytes(byte_hh_r, 'big') 
            hh_imag = int.from_bytes(byte_hh_i, 'big')
            signal[i, j] = hh_real + hh_imag * 1j
    else:
        # paralell processing
        byte_ri = f.read(NUM_PIXEL * 2)
        ri = np.frombuffer(byte_ri, dtype=np.uint8)
        ln = int(len(ri)/2)
        signal[i, :ln] = ri[0::2] + ri[1::2] * 1j
        
    # right offset
    _ = f.read(NUM_BLANK_PIXEL * 2)
    
f.close()


# ## Read `LED` File
f = open(PATH_LED, "rb")


# ### 表3.3-4 SARリーダーファイルディスクリプタレコード
f.seek(8)
record_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
f.seek(180)
summary_record = int(f.read(INTERGER6))
print('25 181 － 186 I6 データセットサマリレコードの数 = bbbbb1 ->', summary_record)
f.seek(186)
summary_record_length = int(f.read(INTERGER6))
print('26 187 － 192 I6 データセットサマリレコード長 = b4096 ->', summary_record_length)
f.seek(192)
map_record = int(f.read(INTERGER6))
print('27 193 － 198 I6 地図投影データレコードの数 = bbbbb0 ->', map_record)
f.seek(198)
map_record_length = int(f.read(INTERGER6))
print('28 199 － 204 I6 地図投影データレコード長 = bbbbb0 ->', map_record_length)
f.seek(210)
platform_record_length = int(f.read(INTERGER6))
print('30 211 － 216 I6 プラットフォーム位置データレコード長 = b4680 ->', platform_record_length)
f.seek(222)
attitude_record_length = int(f.read(INTERGER6))
print('32 223 － 228 I6 姿勢データレコード長 = b8192 ->', attitude_record_length)
f.seek(234)
radiometric_record_length = int(f.read(INTERGER6))
print('34 235 － 240 I6 ラジオメトリックデータレコード長 = bbbbb0 ->', radiometric_record_length)
f.seek(246)
radiometric_comp_record_length = int(f.read(INTERGER6))
print('36 247 － 252 I6 ラジオメトリック補償レコード長 = bbbbb0 ->', radiometric_comp_record_length)
f.seek(258)
data_quality_record_length = int(f.read(INTERGER6))
print('38 259 － 264 I6 データ品質サマリレコード長 = bbbbb0 ->', data_quality_record_length)
f.seek(270)
data_histogram_record_length = int(f.read(INTERGER6))
print('40 271 － 276 I6 データヒストグラムレコード長 = bbbbb0 ->', data_histogram_record_length)
f.seek(282)
range_spectrum_record_length = int(f.read(INTERGER6))
print('42 283 － 288 I6 レンジスペクトルレコード長 = bbbbb0 ->', range_spectrum_record_length)
f.seek(294)
dem_record_length = int(f.read(INTERGER6))
print('44 295 － 300 I6 DEMディスクリプタレコード長 = bbbbb0 ->', dem_record_length)
f.seek(342)
calibration_record_length = int(f.read(INTERGER6))
print('52 343 － 348 I6 キャリブレーションレコード長 = b13212 ->', calibration_record_length)


# ### 表3.3-5 データセットサマリレコード
f.seek(record_length + 8)
summary_record_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 データセットサマリレコード長 = 4096）10 ->', summary_record_length)
f.seek(record_length + 20)
scene_id = f.read(FLOAT32).decode('utf-8')
print('9 21 － 52 A32 シーンID ->', scene_id)
f.seek(record_length + 68)
scene_time = f.read(FLOAT32).decode('utf-8')
print('11 69 － 100 A32 シーンセンター時刻 ->', scene_time)
f.seek(record_length + 164)
ellipsoid_model = f.read(FLOAT16).decode('utf-8')
print('16 165 － 180 A16 楕円体モデル ->', ellipsoid_model)
f.seek(record_length + 180)
ellipsoid_radius = float( f.read(FLOAT16))
print('17 181 － 196 F16.7 楕円体の半長径(Km) ->', ellipsoid_radius)
f.seek(record_length + 196)
ellipsoid_short_radius = float( f.read(FLOAT16))
print('18 197 － 212 F16.7 楕円体の短半径(Km) ->', ellipsoid_short_radius)
f.seek(record_length + 212)
earth_mass = float( f.read(FLOAT16))
print('19 213 － 228 F16.7 地球の質量 (10^24 Kg) ->', earth_mass)
f.seek(record_length + 244)
j2 = float(f.read(FLOAT16))
j3 = float( f.read(FLOAT16))
j4 = float( f.read(FLOAT16))
print('21 245 － 260 F16.7 長楕円パラメータ（力学的形状係数 J2項） ->', j2)
print('22 261 － 276 F16.7 長楕円パラメータ（力学的形状係数 J3項） ->', j3)
print('23 277 － 292 F16.7 長楕円パラメータ（力学的形状係数 J4項） ->', j4)
f.seek(record_length + 308)
ellipsoid_mean = f.read(FLOAT16)
print('25 309 － 324 F16.7 シーン中央における楕円上の平均的な地形標高 ->', ellipsoid_mean)
f.seek(record_length + 388)
sar_channel = int(f.read(INTERGER4))
print('31 389 － 392 I4 SARチャネル数 ->', sar_channel)
f.seek(record_length + 396)
sensor_platform = f.read(FLOAT16).decode('utf-8')
print('33 397 － 412 A16 センサプラットフォーム名(ID) ->', sensor_platform)
f.seek(record_length + 500)
LAMBDA = float(f.read(16))
print('波長λ: ', LAMBDA)
f.seek(record_length + 516)
motion_compensation = f.read(BYTE2).decode('utf-8')
print('43 517 － 518 A2 Motion compensation indicator ＝ 00：固定 ->', motion_compensation)
# 00 ： no compensation
# 01 ： on board compensation
# 10 ： in processor compensation
# 11 ： both on board and in processor
f.seek(record_length + 518)
range_pulse_code = f.read(FLOAT16).decode('utf-8')
print('44 519 － 534 A16 レンジパルスコード ->', range_pulse_code)
f.seek(record_length + 534)
range_pulse_amplitude = float(f.read(FLOAT16))
range_pulse_amplitude2 = float(f.read(FLOAT16))
range_pulse_amplitude3 = float(f.read(FLOAT16))
range_pulse_amplitude4 = float(f.read(FLOAT16))
range_pulse_amplitude5 = float(f.read(FLOAT16))
print('45 535 － 550 E16.7 レンジパルス振幅係数1 ノミナル値 ->', range_pulse_amplitude)
print('46 551 － 566 E16.7 レンジパルス振幅係数2 ノミナル値 ->', range_pulse_amplitude2)
print('47 567 － 582 E16.7 レンジパルス振幅係数3 ノミナル値 ->', range_pulse_amplitude3)
print('48 583 － 598 E16.7 レンジパルス振幅係数4 ノミナル値 ->', range_pulse_amplitude4)
print('49 599 － 614 E16.7 レンジパルス振幅係数5 ノミナル値 ->', range_pulse_amplitude5)
f.seek(record_length + 710)
sampling_frequency_mhz = float(f.read(FLOAT16))
print('57 711 － 726 F16.7 サンプリング周波数 (MHz) ノミナル値 ->', sampling_frequency_mhz)
f.seek(record_length + 726)
range_gate = float(f.read(FLOAT16))
print('58 727 － 742 F16.7 レンジゲート（画像開始時の立ち上がり）(μsec) ->', range_gate)
f.seek(record_length + 742)
range_pulse_width = float(f.read(FLOAT16))
print('59 743 － 758 F16.7 レンジパルス幅 (μsec) ->', range_pulse_width)
f.seek(record_length + 806)
quantization_descriptor = f.read(12).decode('utf-8')
print('65 807 － 818 A12 量子化記述子 ->', quantization_descriptor)
f.seek(record_length + 818)
DC_BIAS_I = float(f.read(FLOAT16))
DC_BIAS_Q = float(f.read(FLOAT16))
gain_imbalance = float(f.read(FLOAT16))
print('66 819 － 834 F16.7 Ｉ成分のＤＣバイアス ノミナル値 ->', DC_BIAS_I)
print('67 835 － 850 F16.7 Ｑ成分のＤＣバイアス ノミナル値 ->', DC_BIAS_Q)
print('68 851 － 866 F16.7 ＩとＱのゲイン不均衡 ノミナル値 ->', gain_imbalance)
f.seek(record_length + 898)
electronic_boresight = float(f.read(FLOAT16))
print('71 899 － 914 F16.7 electronic boresight ->', electronic_boresight)
f.seek(record_length + 914)
mechanical_boresight = float(f.read(FLOAT16))
print('72 915 － 930 F16.7 mechanical boresight ->', mechanical_boresight)
f.seek(record_length + 934)
prf = float(f.read(FLOAT16))
print('74 935 － 950 F16.7 PRF (mHz) ->', prf)
f.seek(record_length + 950)
beam_width_elevation = float(f.read(FLOAT16))
beam_width_azimuth = float(f.read(FLOAT16))
print('75 951 － 966 F16.7 2ウェイアンテナビーム幅(エレベーション、実効値) ノミナル値 ->', beam_width_elevation)
print('76 967 － 982 F16.7 2ウェイアンテナビーム幅(アジマス、実効値) ノミナル値 ->', beam_width_azimuth)
f.seek(record_length + 982)
binary_time = int(f.read(FLOAT16))
clock_time = f.read(FLOAT32).decode('utf-8')
clock_increase = int(f.read(FLOAT16))
print('77 983 － 998 I16 衛星のバイナリ時刻コード： 時刻誤差情報の基準衛星時刻カウンタ(Tref) ->', binary_time)
print('78 999 － 1030 A32 衛星のクロック時刻 ：時刻誤差情報の基準地上時刻(Tgref) ->', clock_time)
print('79 1031 － 1046 I16 衛星のクロックの増加量 [nsec] ：時刻誤差情報の算出衛星カウンタ周期(Psc) ->', clock_increase)
f.seek(record_length + 1174)
# look_azimuth = float(f.read(FLOAT16))
# print('87 1175 － 1190 F16.7 アジマス方向のルック数 ->', look_azimuth) # Blank
f.seek(record_length + 1534)
time_index = f.read(8).decode('utf-8')
print('108 1535 － 1542 A8 ライン方向に沿った時間方向指標（計画値） ->', time_index)
# 1シーン内でＰＲＦが変化していない場合 ="bbb0"
# 1シーン内でＰＲＦが変化した場合 ="bbb1"
# 広観測域モードの場合
f.seek(record_length + 1802)
prf_change_flag = f.read(INTERGER4).decode('utf-8')
print('130 1803 － 1806 I4 PRF変化点フラグ ->', prf_change_flag)
# 変化点なしの場合は、'bbbbbbb1'が格納される。
# 広観測域モードの場合は、'bbbbbbb0'が格納される。
f.seek(record_length + 1806)
prf_change_line = int(f.read(8))
print('131 1807 － 1814 I8 PRF変化開始ライン番号 ->', prf_change_line)
# ヨーステアリングしていない場合 = "bbb1"
# ヨーステアリングしている場合 = "bbb0"
f.seek(record_length + 1830)
yaw_steering_flag = f.read(INTERGER4).decode('utf-8')
print('133 1831 － 1834 I4 ヨーステアリングの有無フラグ ->', yaw_steering_flag)
f.seek(record_length + 1838)
off_nadir_angle = float(f.read(FLOAT16))
print('135 1839 － 1854 F16.7 オフナディア角 ->', off_nadir_angle)
f.seek(record_length + 1854)
antenna_beam_number = int(f.read(INTERGER4))
print('136 1855 － 1858 I4 アンテナビーム番号 ->', antenna_beam_number)


# ### 表3.3-6 プラットフォーム位置データ・レコード
f.seek(record_length + summary_record_length + 8)
platform_record_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 プラットフォーム位置データレコード長 ＝ 4680）10 ->', platform_record_length)
# ALOS軌道情報（予測値） ： '0bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
# ALOS軌道情報（決定値） ： '1bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
# ALOS高精度軌道情報 ： '2bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
f.seek(record_length + summary_record_length + 12)
orbit_type = f.read(FLOAT32).decode('utf-8')
print('7 13 － 44 A32 軌道要素種類 ->', orbit_type)
# ALOS軌道情報（予測値） ： 'bb28'
# ALOS軌道情報（決定値） ： 'bb28'
# ALOS高精度軌道情報 ： 'bb28'
f.seek(record_length + summary_record_length + 140)
NUM_ORB_POINT = int(f.read(INTERGER4))
print('14 141 － 144 I4 データポイント数 ->', NUM_ORB_POINT)
f.seek(record_length + summary_record_length + 144)
TIME_ORB_YEAR = int(f.read(INTERGER4))
TIME_ORB_MONTH = int(f.read(INTERGER4))
TIME_ORB_DAY = int(f.read(INTERGER4))
TIME_ORB_COUNT_DAY = int(f.read(INTERGER4))
TIME_ORB_SEC = float(f.read(FLOAT22))
print('15 145 － 148 I4 第1ポイントの年 ->', TIME_ORB_YEAR)
print('16 149 － 152 I4 第1ポイントの月 ->', TIME_ORB_MONTH)
print('17 153 － 156 I4 第1ポイントの日 ->', TIME_ORB_DAY)
print('18 157 － 160 I4 第1ポイントの通算日 ->', TIME_ORB_COUNT_DAY)
print('19 161 － 182 E22.15 第1ポイントの通算秒 ->', TIME_ORB_SEC)
f.seek(record_length + summary_record_length + 182)
TIME_INTERVAL = float(f.read(FLOAT22))
print('20 183 － 204 E22.15 ポイント間のインターバル時間（秒） ->', TIME_INTERVAL)
f.seek(record_length + summary_record_length + 204)
reference_coordinate = f.read(FLOAT64).decode('utf-8')
print('21 205 － 268 A64 参照座標系 (ECI、ECR) ->', reference_coordinate)
f.seek(record_length + summary_record_length + 290)
position_error = float(f.read(FLOAT16))
print('23 291 － 306 F16.7 進行方向の位置誤差 [m]ノミナル値 ->', position_error)
f.seek(record_length + summary_record_length + 306)
position_error2 = float(f.read(FLOAT16))
print('24 307 － 322 F16.7 直交方向の位置誤差 [m]ノミナル値 ->', position_error2)
f.seek(record_length + summary_record_length + 322)
position_error3 = float(f.read(FLOAT16))
print('25 323 － 338 F16.7 半径方向の位置誤差 [m]ノミナル値 ->', position_error3)
f.seek(record_length + summary_record_length + 338)
velocity_error = float(f.read(FLOAT16))
print('26 339 － 354 F16.7 進行方向の速度誤差 [m/sec]ノミナル値 ->', velocity_error)
f.seek(record_length + summary_record_length + 354)
velocity_error2 = float(f.read(FLOAT16))
print('27 355 － 370 F16.7 直交方向の速度誤差 [m/sec]ノミナル値 ->', velocity_error2)
f.seek(record_length + summary_record_length + 370)
velocity_error3 = float(f.read(FLOAT16))
print('28 371 － 386 F16.7 半径方向の速度誤差 [m/sec]ノミナル値 ->', velocity_error3)
f.seek(record_length + summary_record_length + 386)
position_vector = np.zeros((28, 3))
velocity_vector = np.zeros((28, 3))
for i in range(28):
    position_vector[i, 0] = float(f.read(FLOAT22))
    position_vector[i, 1] = float(f.read(FLOAT22))
    position_vector[i, 2] = float(f.read(FLOAT22))
    velocity_vector[i, 0] = float(f.read(FLOAT22))
    velocity_vector[i, 1] = float(f.read(FLOAT22))
    velocity_vector[i, 2] = float(f.read(FLOAT22))
print('29 387 － 452 E22.15 第1データポイント位置ベクトル (x) [m] ->', position_vector[0, 0])
print('30 387 － 452 E22.15 第1データポイント位置ベクトル (y) [m] ->', position_vector[0, 1])
print('31 387 － 452 E22.15 第1データポイント位置ベクトル (z) [m] ->', position_vector[0, 2])
print('32 453 － 518 E22.15 第28データポイント速度ベクトル(x\') [m/sec] ->', velocity_vector[-1, 0])
print('33 453 － 518 E22.15 第28データポイント速度ベクトル(y\') [m/sec] ->', velocity_vector[-1, 1])
print('34 453 － 518 E22.15 第28データポイント速度ベクトル(z\') [m/sec] ->', velocity_vector[-1, 2])
f.seek(record_length + summary_record_length + 4100)
leap_second_flag = int(f.read(BYTE1))
print('36 4101 － 4101 I1 うるう秒発生フラグ 0：無し、1：うるう秒あり ->', leap_second_flag)

f.seek(record_length + summary_record_length + platform_record_length + 8)
attitude_record_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 姿勢データ・レコード長 ＝ 8192）10 ->', attitude_record_length)
f.seek(record_length + summary_record_length + platform_record_length + 28)
pitch_quality = f.read(INTERGER4).decode('utf-8')
roll_quality = f.read(INTERGER4).decode('utf-8')
yaw_quality = f.read(INTERGER4).decode('utf-8')
pitch = float(f.read(14))
roll = float(f.read(14))
yaw = float(f.read(14))
pitch_rate_quality = f.read(INTERGER4).decode('utf-8')
roll_rate_quality = f.read(INTERGER4).decode('utf-8')
yaw_rate_quality = f.read(INTERGER4).decode('utf-8')
print('10 29 － 32 I4 ピッチ・データ品質フラグ ->', pitch_quality)
print('11 33 － 36 I4 ロール・データ品質フラグ ->', roll_quality)
print('12 37 － 40 I4 ヨー・データ品質フラグ ->', yaw_quality)
print('13 41 － 54 E14.6 ピッチ（度） ->', pitch)
print('14 55 － 68 E14.6 ロール（度） ->', roll)
print('15 69 － 82 E14.6 ヨー（度） ->', yaw)
f.seek(record_length + summary_record_length + platform_record_length + 12)
point_number = int(f.read(INTERGER4))
print('7 13 － 16 I4 ポイント数 ->', point_number)
f.seek(record_length + summary_record_length + platform_record_length + 94)
points_pitches = np.zeros(point_number)
points_rolls = np.zeros(point_number)
points_yaws = np.zeros(point_number)
for i in range(point_number-1):
    points_pitches[i] = float(f.read(14))
    points_rolls[i] = float(f.read(14))
    points_yaws[i] = float(f.read(14))
    break
print('19 95 － 108 E14.6 ピッチ率 ->', points_pitches)
print('20 109 － 122 E14.6 ロール率 ->', points_rolls)
print('21 123 － 136 E14.6 ヨー率 ->', points_yaws)


# ### 表3.3-8 キャリブレーションデータレコード
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + 8)
calibration_record_length = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 レコード長 ＝ 13212）10 ->', calibration_record_length)
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + 16)
valid_sample = int(f.read(INTERGER4))
calibration_start = f.read(17).decode('utf-8')
calibration_end = f.read(17).decode('utf-8')
attenuator = int(f.read(INTERGER4))
alc = int(f.read(BYTE1))
agc = int(f.read(BYTE1))
pulse_width = int(f.read(INTERGER4))
chirp_bandwidth = int(f.read(INTERGER4))
sampling_frequency = int(f.read(INTERGER4))
quantization_bit = int(f.read(INTERGER4))
chirp_replica = int(f.read(INTERGER4))
chirp_replica_line = int(f.read(INTERGER4))
print('8 17 － 20 I4 有効サンプル数=Nsamp ->', valid_sample)
print('9 21 － 37 A17 校正データ取得開始時刻 ->', calibration_start)
print('10 38 － 54 A17 校正データ取得終了時刻 ->', calibration_end)
print('11 55 － 58 I4 校正器ATT設定値 ->', attenuator)
print('12 59 － 59 I1 校正器ALC ->', alc)
print('13 60 － 60 I1 AGC/MGC ->', agc)
print('14 61 － 64 I4 送信パルス幅 ->', pulse_width)
print('15 65 － 68 I4 チャープ帯域 ->', chirp_bandwidth)
print('16 69 － 72 I4 サンプリング周波数 ->', sampling_frequency)
print('17 73 － 76 I4 量子化ビット数 ->', quantization_bit)
print('18 77 － 80 I4 チャープレプリカデータ数 ->', chirp_replica)
print('19 81 － 84 I4 チャープレプリカデータ積算ライン数ｎ ->', chirp_replica_line)
# 20 85 － 85 I1 受信偏波1 0=H偏波、1=V偏波
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + 84)
receive_polarization1 = int(f.read(BYTE1))
print('20 85 － 85 I1 受信偏波1 ->', receive_polarization1)
# 21 86 － α Nsamp*(2B2)
# チャープレプリカデータ1
# 取得した第1フレーム～ｎフレーム目の各サンプル毎の合計値
# （ΣI1(n)、ΣＱ1(n)、ΣI2(n)、ΣQ2(n)…・,ΣINsamp(n)、ΣＱNsamp(n)の順）
# （1サンプル（I,Q）各16ビット整数値）
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + 85)
chirp_replica_data1 = np.zeros((valid_sample, 2))
for i in range(valid_sample):
    chirp_replica_data1[i, 0] = int.from_bytes(f.read(BYTE2), byteorder="big")
    chirp_replica_data1[i, 1] = int.from_bytes(f.read(BYTE2), byteorder="big")
print('21 86 － α Nsamp*(2B2) チャープレプリカデータ1 ->', chirp_replica_data1.shape)
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + 6230)
# receive_polarization2 = int(f.read(BYTE1)) # blank
# print('22 6231 － 6231 I1 受信偏波2 ->', receive_polarization2)


# 
# ### 表3.3-9 設備関連データレコード


# TT&Cシステムテレメトリデータ = 1,540,000）10
# 姿勢決定3、GPSR生データ = 4,314,000）10
# PALSARミッションテレメトリデータ = 345,000）10
# ALOS軌道情報：予測値（ECR) = 325,000）10
# ALOS軌道情報：決定値（ECR) = 325,000）10
# 時刻誤差情報 = 3,072）10
# ALOS高精度軌道情報 = 511,000）10
# 高精度姿勢情報 = 4,370,000）10
# 座標変換情報 = 728,000）10
# ワークオーダ&ワークレポート = 15,000）10
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + calibration_record_length + 0)
record_order = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('1 1 － 4 B4 レコード順序番号 ->', record_order)

f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + calibration_record_length + 7)
sub_type = int.from_bytes(f.read(BYTE1), byteorder="big")
print('5 8 － 8 B1 第3レコードサブタイプコード (JAXA=70)->', sub_type)

# CEOS=20、CCRS=36、ESA=50、NASA=60、JPL=61
# JAXA=70、DFVLR=80、RAE=90、TELESPAZIO=10
# UNSPECIFIED=18、等
f.seek(record_length + summary_record_length + platform_record_length + attitude_record_length + calibration_record_length + 8) # 31484
atla_record_length1 = int.from_bytes(f.read(INTERGER4), byteorder="big")
print('6 9 － 12 B4 レコード長 ->', atla_record_length1) # TT&Cシステムテレメトリデータ = 1,540,000
# 以降はブランクなので割愛


# # ALOS Pramameter
# 


NUM_INTERPOLATION_DIM = 9 
NUM_CHIRP_EXTENTION = 1000
NUM_OFFICIALAXA_L11_AREA = 9216 # Reference from L1.1
TIME_SHIFT = 0
DIS_AZIMUTH_RESOLUTION = 5
CREDIT = ' ©JAXA, METI'
IS_PLOT = False


# # Parameter
# CEOS フォーマットから読み込んだ値から算出する位置関係や周波数。


TIME_PLUSE_DURATION = chirp_length * 1e-9
FREQ_AD_SAMPLE = sampling_frequency * 1e6
FREQ_RANGE_CHIRP_RATE = -(chirp_bandwidth * 1e6) / TIME_PLUSE_DURATION
FREQ_PULSE_REPETATION = prf * 1e-3
DIS_RANGE_SLANT = SOL / (2. * FREQ_AD_SAMPLE)
NUN_FFT_RANGE = 2 ** math.ceil(math.log2(NUM_PIXEL))
NUM_APERTURE_SAMPLE = NUM_SIGNAL_RECORD # sythetic aperture length
NUM_RANGE = NUM_PIXEL + NUM_CHIRP_EXTENTION
NUM_CHIRP_SAMPLE = int(FREQ_AD_SAMPLE * TIME_PLUSE_DURATION)
NUM_CHIRP_SAMPLE_HALF = int(NUM_CHIRP_SAMPLE / 2)
NUM_RCMC_SCALE_BIN = 13
NUM_VEOCITY_CALC_SPAN_COUNT_BIN = 2
NUM_VEOCITY_CALC_SAMPLE = 6
DIS_ELLIPSOID_RADIUS = ellipsoid_radius * 1e3
DIS_ELLIPSOID_SHORT_RADIUS = ellipsoid_short_radius * 1e3
NUM_VEOCITY_CALC_SPAN_COUNT = 2 ** NUM_VEOCITY_CALC_SPAN_COUNT_BIN
NUM_POLYNOMIAL_COEFFICIENT_DIM = 3
assert NUM_POLYNOMIAL_COEFFICIENT_DIM > 1, 'NUM_POLYNOMIAL_COEFFICIENT_DIM must be greater than 1'



# JSONデータ作成
parameters = {
    "NUM_INTERPOLATION_DIM": NUM_INTERPOLATION_DIM,
    "NUM_CHIRP_EXTENTION": NUM_CHIRP_EXTENTION,
    "NUM_OFFICIALAXA_L11_AREA": NUM_OFFICIALAXA_L11_AREA,
    "TIME_SHIFT": TIME_SHIFT,
    "TIME_PLUSE_DURATION": TIME_PLUSE_DURATION,
    "FREQ_AD_SAMPLE": FREQ_AD_SAMPLE,
    "FREQ_RANGE_CHIRP_RATE": FREQ_RANGE_CHIRP_RATE,
    "FREQ_PULSE_REPETATION": FREQ_PULSE_REPETATION,
    "DIS_RANGE_SLANT": DIS_RANGE_SLANT,
    "NUN_FFT_RANGE": NUN_FFT_RANGE,
    "NUM_APERTURE_SAMPLE": NUM_APERTURE_SAMPLE,
    "NUM_RANGE": NUM_RANGE,
    "NUM_CHIRP_SAMPLE": NUM_CHIRP_SAMPLE,
    "NUM_CHIRP_SAMPLE_HALF": NUM_CHIRP_SAMPLE_HALF,
    "NUM_RCMC_SCALE_BIN": NUM_RCMC_SCALE_BIN,
    "NUM_VEOCITY_CALC_SPAN_COUNT_BIN": NUM_VEOCITY_CALC_SPAN_COUNT_BIN,
    "NUM_VEOCITY_CALC_SAMPLE": NUM_VEOCITY_CALC_SAMPLE,
    "DIS_ELLIPSOID_RADIUS": DIS_ELLIPSOID_RADIUS,
    "DIS_ELLIPSOID_SHORT_RADIUS": DIS_ELLIPSOID_SHORT_RADIUS,
    "NUM_VEOCITY_CALC_SPAN_COUNT": NUM_VEOCITY_CALC_SPAN_COUNT,
    "DIS_AZIMUTH_RESOLUTION": DIS_AZIMUTH_RESOLUTION,
    "CREDIT": CREDIT,
    "IS_PLOT": IS_PLOT,
    "NUM_POLYNOMIAL_COEFFICIENT_DIM": NUM_POLYNOMIAL_COEFFICIENT_DIM,
}

# JSONファイルに保存
with open(os.path.join( PATH_OUTPUT, "parameters.json"), "w") as f:
    json.dump(parameters, f, indent=2)
    print("Parameters saved to parameters.json ->", parameters)

print("\n合成開口を始めるわよ!  ...")
# calculate time
start_time = time.time()


# # Range Compression
# ## Reference
ref_range = np.zeros(NUN_FFT_RANGE, dtype=np.complex128)

time_chirp = np.divide(
    np.arange(-NUM_CHIRP_SAMPLE_HALF, NUM_CHIRP_SAMPLE_HALF),
    FREQ_AD_SAMPLE)
phase = FREQ_RANGE_CHIRP_RATE * time_chirp**2 * np.pi
ref_range[:NUM_CHIRP_SAMPLE] = np.exp(1j * phase)

if IS_PLOT:
    plt.figure(figsize=(16, 3), dpi=70, facecolor='w', edgecolor='k')
    plt.title("Chirp Signal", fontsize=16,)
    plt.plot(ref_range.real, label="I", alpha=0.7)
    plt.plot(ref_range.imag, label="Q", alpha=0.7)
    plt.xlabel("Range Sample [n]")
    plt.ylabel("Amplitude [I/Q]")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "chirp_signal_range.png"), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()

if IS_PLOT:
    plt.figure(figsize=(16, 4), dpi=100, facecolor='w', edgecolor='k')
    plt.title("Chirp Signal", fontsize=16,)
    plt.plot(time_chirp, ref_range[:NUM_CHIRP_SAMPLE].real, label="I", alpha=0.7)
    plt.plot(time_chirp, ref_range[:NUM_CHIRP_SAMPLE].imag, label="Q", alpha=0.7)
    plt.xlabel("Time [sec]")
    plt.ylabel("Amplitude [I/Q]")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "chirp_signal.png"), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()


ref_range = np.roll(ref_range, -NUM_CHIRP_EXTENTION)
ref_range_fft = np.fft.fft(ref_range, n=NUN_FFT_RANGE)

if IS_PLOT:
    plt.figure(figsize=(16, 4), 
            dpi=100, facecolor='w', edgecolor='k'
            )
    plt.title("Reference FFT Amplitude")
    plt.plot(np.abs(ref_range_fft), label="Reference FFT")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "chirp_signal_fft_range_amp.png"), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()

if IS_PLOT:
    plt.figure(figsize=(16, 4), dpi=100, facecolor='w', edgecolor='k')
    plt.title("Reference FFT")
    plt.plot(ref_range_fft.real, label="Reference I", alpha=0.7)
    plt.plot(ref_range_fft.imag, label="Reference Q", alpha=0.7)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    # plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "chirp_signal_fft_range.png"), bbox_inches='tight', 
                format='png', dpi=160
                )
    # plt.show();
    plt.clf();plt.close()

ref_range_fft = np.conjugate(ref_range_fft) / NUN_FFT_RANGE


data_raw = np.zeros((NUM_SIGNAL_RECORD, NUN_FFT_RANGE), dtype=np.complex128)
data_raw[:, :NUM_PIXEL] = signal - (DC_BIAS_I + 1j * DC_BIAS_Q)
print("RAW Data Align Processed ->", data_raw.shape)

if IS_PLOT:
    plt.figure(figsize=(16, 10),dpi=100, 
            facecolor='w', edgecolor='k')
    plt.title("Raw Data")
    plt.imshow(np.abs(data_raw[:NUM_APERTURE_SAMPLE]))
    plt.xlabel("Range Sample [n]")
    plt.ylabel("Signal Record")
    plt.colorbar(shrink=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "data_raw_plot.png"), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()
    
plt.imsave(os.path.join(PATH_OUTPUT, "data_raw.png"), np.abs(data_raw), cmap='gray')


# ## Pulse Compression


for idx_record in tqdm(range(NUM_SIGNAL_RECORD), desc="Pulse Compression ...", smoothing=.15):
    data_raw[idx_record] = np.fft.fft(data_raw[idx_record], n=NUN_FFT_RANGE) * ref_range_fft
    # edge padding
    data_raw[idx_record, -NUM_CHIRP_EXTENTION:] = 0
    data_raw[idx_record, :NUM_CHIRP_EXTENTION] = 0

if IS_PLOT:
    plt.figure(figsize=(16, 8), dpi=100, facecolor='w', edgecolor='k')
    plt.subplot(2, 1, 1)
    plt.title("Pulse Compression FFT")
    plt.plot(data_raw[-1].real, label="Pulse Compressed I", alpha=0.7)
    plt.plot(data_raw[-1].imag, label="Pulse Compressed Q", alpha=0.7)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.title("Pulse Compression FFT")
    plt.plot(np.abs(data_raw[0]), label="Pulse Compressed Amplitude")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "pulse_compression_fft.png"), bbox_inches='tight', 
                format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()

for idx_record in tqdm(range(NUM_SIGNAL_RECORD), desc="IFFT ...", smoothing=.15):
    data_raw[idx_record] = np.fft.ifft(data_raw[idx_record], n=NUN_FFT_RANGE)

if IS_PLOT:
    plt.figure(figsize=(16, 8), dpi=100, facecolor='w', edgecolor='k')
    plt.subplot(2, 1, 1)
    plt.title("Pulse Compression IFFT")
    plt.plot(data_raw[600].real, label="Pulse Compressed I", alpha=0.7)
    plt.plot(data_raw[600].imag, label="Pulse Compressed Q", alpha=0.7)
    plt.xlabel("Range Sample [n]")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.title("Pulse Compression IFFT")
    plt.plot(np.abs(data_raw[0]), label="Pulse Compressed Amplitude")
    plt.xlabel("Range Sample [n]")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "pulse_compression.png"), bbox_inches='tight', 
                format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()


elapsed_time = time.time() - start_time
print(f"パルス圧縮処理時間: {elapsed_time:.6f} 秒")


if IS_PLOT:
    plt.figure(figsize=(16, 10),dpi=100, 
            facecolor='w', edgecolor='k')
    plt.title("Range Compression Data")
    plt.imshow(np.abs(data_raw[:NUM_APERTURE_SAMPLE]), vmax=0.1)
    plt.xlabel("Range Sample [n]")
    plt.ylabel("Signal Record")
    plt.colorbar(shrink=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "data_range_compression_plot.png"), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()
    
plt.imsave(os.path.join(PATH_OUTPUT, "data_range_comp.png"), np.abs(data_raw[:NUM_APERTURE_SAMPLE]), cmap='gray')


# # Azimuth Compression
# 
# ### observation time


# cast to float64
TIME_OBS_START_DAY = np.array(TIME_OBS_START_DAY, dtype=np.float64)
TIME_OBS_START_MSEC = np.array(TIME_OBS_START_MSEC, dtype=np.float64)
TIME_OBS_END_DAY = np.array(TIME_OBS_END_DAY, dtype=np.float64)
TIME_OBS_END_MSEC = np.array(TIME_OBS_END_MSEC, dtype=np.float64)

TIME_OBS_START_ = TIME_OBS_START_DAY + (TIME_OBS_START_MSEC / DIGIT4 + TIME_SHIFT)/TIME_DAY_SEC
TIME_OBS_START_CENTER_SEC = TIME_DAY_SEC * TIME_OBS_START_ + 0.5 * (NUM_APERTURE_SAMPLE - NUM_OFFICIALAXA_L11_AREA) / FREQ_PULSE_REPETATION
TIME_OBS_END_CENTER_SEC = TIME_OBS_START_CENTER_SEC + NUM_OFFICIALAXA_L11_AREA / FREQ_PULSE_REPETATION * 3

time_orbit = np.arange(TIME_DAY_SEC * TIME_ORB_COUNT_DAY + TIME_ORB_SEC, 
                       TIME_DAY_SEC * TIME_ORB_COUNT_DAY + TIME_ORB_SEC + TIME_INTERVAL * NUM_ORB_POINT, 
                       TIME_INTERVAL)
num_orb_counts = np.arange(0, NUM_ORB_POINT, 1)

func_intp_orbit_x_recode_time = interp1d(time_orbit, position_vector[:, 0], kind='cubic', axis=0)
func_intp_orbit_y_recode_time = interp1d(time_orbit, position_vector[:, 1], kind='cubic', axis=0)
func_intp_orbit_z_recode_time = interp1d(time_orbit, position_vector[:, 2], kind='cubic', axis=0)

if IS_PLOT:
    plt.figure(figsize=(12, 4), dpi=80, facecolor='w', edgecolor='k')
    plt.title('ALOS PALSAR TimeSeries')
    plt.scatter(num_orb_counts, time_orbit, label='Orbit Recording Point')
    plt.plot(num_orb_counts, time_orbit, label='Orbit Recording Line', linestyle='-', color='b')
    # hrizontal line
    plt.axhline(y=TIME_OBS_START_CENTER_SEC, color='r', linestyle='-', label='Start time')
    plt.axhline(y=TIME_OBS_END_CENTER_SEC, color='g', linestyle='--', label='End time')
    plt.legend(loc='upper left')

    plt.xlabel('Sample Count [n]')
    plt.ylabel('Time [sec]')
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, f'orbit_timeseries.png'), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()


# ### Geometory


TIME_OBS_CMD_CENTER = (TIME_OBS_START_CENTER_SEC + TIME_OBS_END_CENTER_SEC) / 2.0
time_delta_center_start = TIME_OBS_CMD_CENTER - (NUM_VEOCITY_CALC_SPAN_COUNT/2)
time_delta_center_end = TIME_OBS_CMD_CENTER + (NUM_VEOCITY_CALC_SPAN_COUNT/2)

p_sat_center_x = func_intp_orbit_x_recode_time(TIME_OBS_CMD_CENTER)
p_sat_center_y = func_intp_orbit_y_recode_time(TIME_OBS_CMD_CENTER)
p_sat_center_z = func_intp_orbit_z_recode_time(TIME_OBS_CMD_CENTER)
p_sat_center_xyz = np.sqrt(p_sat_center_x**2 + p_sat_center_y**2 + p_sat_center_z**2)

p_sat_delta_pre_center_x = func_intp_orbit_x_recode_time(time_delta_center_start)
p_sat_delta_pre_center_y = func_intp_orbit_y_recode_time(time_delta_center_start)
p_sat_delta_pre_center_z = func_intp_orbit_z_recode_time(time_delta_center_start)
p_sat_delta_post_center_x = func_intp_orbit_x_recode_time(time_delta_center_end)
p_sat_delta_post_center_y = func_intp_orbit_y_recode_time(time_delta_center_end)
p_sat_delta_post_center_z = func_intp_orbit_z_recode_time(time_delta_center_end)

v_sat_center_x = (p_sat_delta_post_center_x - p_sat_delta_pre_center_x) / NUM_VEOCITY_CALC_SPAN_COUNT
v_sat_center_y = (p_sat_delta_post_center_y - p_sat_delta_pre_center_y) / NUM_VEOCITY_CALC_SPAN_COUNT
v_sat_center_z = (p_sat_delta_post_center_z - p_sat_delta_pre_center_z) / NUM_VEOCITY_CALC_SPAN_COUNT
v_sat_center_xyz = np.sqrt(v_sat_center_x**2 + v_sat_center_y**2 + v_sat_center_z**2)

p_sat_center_xyz_3dim = np.array([p_sat_center_x, p_sat_center_y, p_sat_center_z], dtype=np.float64) / p_sat_center_xyz
v_sat_center_xyz_3dim = np.array([v_sat_center_x, v_sat_center_y, v_sat_center_z], dtype=np.float64) / v_sat_center_xyz
p_sat_cross_product_3dim = np.array([
    p_sat_center_xyz_3dim[1] * v_sat_center_xyz_3dim[2] - p_sat_center_xyz_3dim[2] * v_sat_center_xyz_3dim[1],
    p_sat_center_xyz_3dim[2] * v_sat_center_xyz_3dim[0] - p_sat_center_xyz_3dim[0] * v_sat_center_xyz_3dim[2],
    p_sat_center_xyz_3dim[0] * v_sat_center_xyz_3dim[1] - p_sat_center_xyz_3dim[1] * v_sat_center_xyz_3dim[0]
])

p_sat_latitude = np.arcsin(p_sat_center_z / p_sat_center_xyz)
sin_sat_latitude, cos_sat_latitude = np.sin(p_sat_latitude), np.cos(p_sat_latitude)
p_earth_radius = np.divide(1.,
                           np.sqrt(
                               cos_sat_latitude**2 / DIS_ELLIPSOID_RADIUS**2 +
                               sin_sat_latitude**2 / DIS_ELLIPSOID_SHORT_RADIUS**2
                           ))

theta_sat_center_cosine_law = (p_sat_center_xyz**2 + DIS_NEAR_RANGE**2 - p_earth_radius **2) / (2. * p_sat_center_xyz * DIS_NEAR_RANGE)
theta_sat_center_sin = np.sin(np.arccos(theta_sat_center_cosine_law))

p_earth_radius_center_x = p_sat_center_x + DIS_NEAR_RANGE * \
    (-theta_sat_center_sin * p_sat_cross_product_3dim[0] - theta_sat_center_cosine_law * p_sat_center_xyz_3dim[0])
p_earth_radius_center_y = p_sat_center_y + DIS_NEAR_RANGE * \
    (-theta_sat_center_sin * p_sat_cross_product_3dim[1] - theta_sat_center_cosine_law * p_sat_center_xyz_3dim[1])
p_earth_radius_center_z = p_sat_center_z + DIS_NEAR_RANGE * \
    (-theta_sat_center_sin * p_sat_cross_product_3dim[2] - theta_sat_center_cosine_law * p_sat_center_xyz_3dim[2])

num_tmp_sample = 33
idx_tmp_center = np.arange(0, num_tmp_sample, 1, dtype=np.int64) - num_tmp_sample / 2
time_tmp_center = 2 * idx_tmp_center * 100 / FREQ_PULSE_REPETATION
time_tmp_start0 = TIME_OBS_CMD_CENTER + time_tmp_center
p_sat_center_tmp_x = func_intp_orbit_x_recode_time(time_tmp_start0)
p_sat_center_tmp_y = func_intp_orbit_y_recode_time(time_tmp_start0)
p_sat_center_tmp_z = func_intp_orbit_z_recode_time(time_tmp_start0)

P_DIFFERENCE_FLAT_SLANT = np.sqrt(
    (p_earth_radius_center_x - p_sat_center_tmp_x)**2 + \
    (p_earth_radius_center_y - p_sat_center_tmp_y)**2 + \
    (p_earth_radius_center_z - p_sat_center_tmp_z)**2
    ) - DIS_NEAR_RANGE

if IS_PLOT:
    plt.figure(figsize=(12, 4),  facecolor='w', edgecolor='k')
    plt.plot(time_tmp_center, P_DIFFERENCE_FLAT_SLANT, label="Slant Range Curve from Earth [m]")
    plt.xlabel("Time [s]")
    plt.ylabel("Difference Distance [m]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT,f'slant_range_center_curve.png'))
    # plt.show();
    plt.clf();plt.close()

# Vandermonde matrix
van = np.vander(time_tmp_center[:NUM_VEOCITY_CALC_SAMPLE], (NUM_POLYNOMIAL_COEFFICIENT_DIM + 1), increasing=True)
# solve equation: (A.T @ A) C = A.T @ Y  van:= A, Y:= P_DIFFERENCE_FLAT_SLANT, T:= time_tmp_center
polynominal_coeff = np.linalg.lstsq(van, P_DIFFERENCE_FLAT_SLANT[:NUM_VEOCITY_CALC_SAMPLE], rcond=None)[0]  # 最小二乗解を求める
v_ground_center = np.sqrt(2. * DIS_NEAR_RANGE * polynominal_coeff[2])

signal_dc = signal - (DC_BIAS_I + 1j * DC_BIAS_Q)
singal_azimuth_shift_diff = np.sum(np.angle(np.sum(signal_dc[:-1].conj() * signal_dc[1:], axis=0)) / (np.pi * 2), axis=0)
freq_doppler_shift = (singal_azimuth_shift_diff / NUM_PIXEL) * FREQ_PULSE_REPETATION
del signal_dc, singal_azimuth_shift_diff
gc.collect()


# ### Frequency 


dis_near_range_extshift = DIS_NEAR_RANGE - NUM_CHIRP_EXTENTION * DIS_RANGE_SLANT
num_velocity_azimuth_shift = v_ground_center / FREQ_PULSE_REPETATION
v_cell_migration_walk = (LAMBDA * FREQ_PULSE_REPETATION) ** 2 / (8.0 * v_ground_center ** 2) # R rd (fη) = R0 (1 + λ^2 f^2 / 8 * Vg^2) の係数
idx_range = np.arange(0, NUM_RANGE, 1, dtype=np.int64)
dis_slant_range = dis_near_range_extshift + DIS_RANGE_SLANT * idx_range
dis_range_migration_curve = np.divide(dis_slant_range,
    (1. + v_cell_migration_walk * (freq_doppler_shift / FREQ_PULSE_REPETATION) ** 2)) 
rate_range_migration_curve =  dis_range_migration_curve / dis_slant_range # = 1 (TODO: Check)

freq_azimuth_doppler_rate = -2.0 * v_ground_center ** 2 * rate_range_migration_curve ** 2 / (LAMBDA * dis_slant_range) # Fη := Ka * η (Ka := -2 * Vg^2  * R0 / λ)
num_azimuth_compression_band = (dis_slant_range * LAMBDA / (4. * num_velocity_azimuth_shift * DIS_AZIMUTH_RESOLUTION)).astype(np.int64)
num_azimuth_shift = (freq_doppler_shift / FREQ_PULSE_REPETATION + 0.5).astype(np.int64)
num_azimuth_shift_start = NUM_APERTURE_SAMPLE * (freq_doppler_shift - num_azimuth_shift * FREQ_PULSE_REPETATION) / FREQ_PULSE_REPETATION
num_azimuth_sample = num_azimuth_shift_start + NUM_APERTURE_SAMPLE // 2 + 1
num_azimuth_sample = np.where(num_azimuth_sample > NUM_APERTURE_SAMPLE, 
                              num_azimuth_sample - NUM_APERTURE_SAMPLE, 
                              num_azimuth_sample)


def rcm_integration_coefficient(num_filter: int, num_integration: int = 9):
    rcm_coeff = np.zeros(num_filter*(num_integration+1), dtype=np.float64)
    # index modulation
    mod_filter = np.repeat(np.arange(num_filter), num_integration)  
    mod_ingegration = np.tile(np.arange(num_integration), num_filter)
    mod_cycle = mod_filter / num_filter
    coef = np.sin(np.pi * mod_cycle) / np.pi
    # rcm coefficient
    coef_center = int(num_integration / 2)
    offset_odd = (num_integration+1) % 2
    coefs = []
    for i in range(-coef_center+offset_odd, 0, 1):
        coefs.append((-i + mod_cycle) * (-1) ** i)
    coefs.append(mod_cycle)
    for i in range(1, coef_center+1, 1):
        coefs.append((i - mod_cycle) * (-1) ** (i+1))
    denom = np.column_stack(coefs)
    # postprocess critical points
    mask = (mod_cycle != 0.) & (mod_cycle != 1.) # aviod dividing by zero 
    indices = mod_filter[mask] * num_integration + mod_ingegration[mask] 
    rcm_coeff[indices] = np.divide(coef[mask], denom[mask, mod_ingegration[mask]])
    indices_zero = mod_filter[mod_cycle == 0.] * num_integration + (coef_center-1)
    rcm_coeff[indices_zero] = 1.
    indices_one = mod_filter[mod_cycle == 1.] * num_integration + coef_center
    rcm_coeff[indices_one] = 1.
    return rcm_coeff

rcm_coeff = rcm_integration_coefficient(2 ** NUM_RCMC_SCALE_BIN, num_integration=NUM_INTERPOLATION_DIM)
DIM_IS_ODD = NUM_INTERPOLATION_DIM % 2
coef_center = int(np.round(NUM_INTERPOLATION_DIM / 2 + 0.5))


# ### Doppler Domain


data_range_comp = data_raw[:NUM_APERTURE_SAMPLE, :]
for idx_range in tqdm(
    range(NUM_RANGE), total=NUM_RANGE, 
    desc="Azimuth FFT to Dopper Domain ...", smoothing=0.15):
    data_range_comp[:, idx_range] = np.fft.fft(data_range_comp[:, idx_range], n=NUM_APERTURE_SAMPLE)


if IS_PLOT:
    percentinel = 20
    v_max = np.max(np.abs(data_range_comp))
    print(f"Max Value -> {v_max}")

    plt.figure(figsize=(18, 10), dpi=100)
    plt.imshow(np.abs(data_range_comp), vmax=v_max * percentinel / 100)
    plt.colorbar(shrink=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, "data_range_compression_dopp_domain_plot.png"), bbox_inches='tight', format='png', dpi=160)
    # plt.show();
    plt.clf();plt.close()


# ### Range Cell Migration Correction


data_rm = np.zeros_like(data_range_comp, dtype=np.complex128)
offset_min = -coef_center + 2
offset = np.arange(offset_min, offset_min+NUM_INTERPOLATION_DIM, 1, dtype=np.int64)
idx_range_rcmc = np.arange(NUM_RANGE, dtype=np.int64)

for idx_line in tqdm(range(NUM_APERTURE_SAMPLE), smoothing=.15,
               total=NUM_APERTURE_SAMPLE , desc="Range Migration..."):
    # only doppler shift case implementaion
    freq_gradient = (idx_line / NUM_APERTURE_SAMPLE) * FREQ_PULSE_REPETATION
    NUM_PRF_STEP = int((freq_gradient-freq_doppler_shift)/FREQ_PULSE_REPETATION + 0.5)
    freq_azimuth_doppler = freq_gradient - NUM_PRF_STEP * FREQ_PULSE_REPETATION
    # rcm pixel
    num_curve_pixel = dis_range_migration_curve * (v_cell_migration_walk / DIS_RANGE_SLANT) * \
        (freq_azimuth_doppler**2 - freq_doppler_shift**2) / FREQ_PULSE_REPETATION**2 + idx_range_rcmc
    num_rcm_step = (num_curve_pixel).astype(np.int64)
    # valid shift indices
    valid_indices = np.full_like(num_rcm_step, False, dtype=bool)
    valid_indices[(num_rcm_step >= -offset_min+1) & (num_rcm_step < (NUM_RANGE - (NUM_INTERPOLATION_DIM + offset_min-1)))] = True
    valid_indices_array = np.where(valid_indices)[0]  # Extract valid indices as array
    # walk and curve
    num_mod_step = (num_curve_pixel - num_rcm_step)[valid_indices_array]
    num_mod_idx = (NUM_INTERPOLATION_DIM * (num_mod_step * 2 ** NUM_RCMC_SCALE_BIN + 0.5).astype(np.int64))
    # get coefficient, get data
    indices_coef = num_mod_idx[:, None] + np.arange(NUM_INTERPOLATION_DIM)
    dis_rcm_coef = rcm_coeff[indices_coef]
    indices_valid_shift = num_rcm_step[valid_indices_array, None] + offset
    data_rcm_shift = data_range_comp[idx_line][indices_valid_shift]
    # Collect and Integrate
    integration_rcm = np.zeros(NUM_RANGE, dtype=np.complex128)
    integration_rcm[valid_indices_array] = (dis_rcm_coef * data_rcm_shift).sum(axis=1)
    data_rm[idx_line, :NUM_RANGE] = integration_rcm # invalid 0 pading

del data_rcm_shift, integration_rcm, valid_indices, valid_indices_array
gc.collect()


elapsed_time = time.time() - start_time
print(f"レンジマイグレーション処理時間: {elapsed_time:.6f} 秒")


if IS_PLOT:
    plt.figure(figsize=(16, 6), dpi=100, 
            facecolor='w', edgecolor='k')
    plt.subplot(2, 1, 1)
    plt.title("Range Cell Migration Result")
    plt.plot(np.abs(data_range_comp[-1]),label="Before Range Migration", alpha=0.7)
    plt.plot(np.abs(data_rm[-1]), label="After Range Migration", alpha=0.7)
    plt.xlim(0, NUM_RANGE)
    plt.legend()
    plt.grid(True)
    plt.subplot(2, 1, 2)
    plt.title("Range Cell Migration details")
    plt.plot(np.abs(data_range_comp[-1][300:500]),label="Before Range Migration", alpha=0.7)
    plt.plot(np.abs(data_rm[-1][300:500]), label="After Range Migration", alpha=0.7)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PATH_OUTPUT, 'range_cell_migration_result.png'))
    # plt.show();
    plt.clf();plt.close()


if IS_PLOT:
    data_rm_patch = data_rm[:4096, :]

    percentinel = 80
    v_max = np.max(np.abs(data_rm_patch))
    print(f"Max Value -> {v_max}")

    plt.figure(figsize=(18, 10), dpi=100)
    plt.imshow(np.abs(data_rm_patch), vmax=6)
    plt.colorbar(shrink=0.5)
    # plt.show();
    plt.clf();plt.close()


# ### Azimuth Compression


data_az  = np.zeros((NUM_APERTURE_SAMPLE, NUM_RANGE), dtype=np.complex128)

# azimuth reference signal
ref_azimuth = np.zeros((NUM_APERTURE_SAMPLE, NUM_RANGE), dtype=np.complex128)
ref_azimuth[0, :] = np.exp(1j * freq_doppler_shift ** 2 * np.pi/ freq_azimuth_doppler_rate)
idx_wing = np.arange(0, num_azimuth_compression_band.max(), 1, dtype=np.int64)

# 2D interpolation
f_rate_ra_az = np.broadcast_to(freq_azimuth_doppler_rate, (NUM_APERTURE_SAMPLE,) + freq_azimuth_doppler_rate.shape)
f0_ra_az = np.broadcast_to(freq_doppler_shift, (NUM_APERTURE_SAMPLE,) + freq_doppler_shift.shape)

time_azimuth = (idx_wing + 1) / FREQ_PULSE_REPETATION
freq_azimuth_doppler_shift = np.pi * f_rate_ra_az[idx_wing].T * time_azimuth ** 2
phase_up = 2 * np.pi * f0_ra_az[idx_wing].T * time_azimuth + freq_azimuth_doppler_shift
phase_dw = - 2 * np.pi * f0_ra_az[idx_wing].T * time_azimuth + freq_azimuth_doppler_shift
ref_azimuth[idx_wing + 1, :] =  np.exp(1j * phase_up.T)
ref_azimuth[-idx_wing + NUM_APERTURE_SAMPLE - 1, :] = np.exp(1j * phase_dw.T)
# azimuth reference furier transform
ref_azimuth_fft = np.fft.fft(ref_azimuth, n=NUM_APERTURE_SAMPLE, axis=0)
ref_azimuth_fft = np.conj(ref_azimuth_fft)
# azimuth compression
idx_azimuth_up = np.arange(0, num_azimuth_sample.max(), 1, dtype=np.int64)
data_az[idx_azimuth_up, :NUM_RANGE] = data_rm[idx_azimuth_up, :NUM_RANGE] * (ref_azimuth_fft[idx_azimuth_up, :])
idx_azimuth_dw = np.arange(NUM_APERTURE_SAMPLE - 1, num_azimuth_sample.max(), -1, dtype=np.int64)
data_az[idx_azimuth_dw, :NUM_RANGE] = data_rm[idx_azimuth_dw, :NUM_RANGE] * (ref_azimuth_fft[idx_azimuth_dw, :])
# convert time domain
data_az[:NUM_APERTURE_SAMPLE, :NUM_RANGE] = np.fft.ifft(data_az, n=NUM_APERTURE_SAMPLE, axis=0)

end_time = time.time()


elapsed_time = end_time - start_time
print(f"合成開口処理時間: {elapsed_time:.6f} 秒")


if IS_PLOT:
    plt.figure(figsize=(10, 6))
    plt.imshow(np.abs(data_az[:2048, :2048]), vmin=0, vmax=10)
    plt.colorbar(shrink=0.5)
    # plt.show();
    plt.clf();plt.close()
    gc.collect()


# # Vizualize 
# 
# intencity histgram
amp = np.abs(data_az[NUM_OFFICIALAXA_L11_AREA:-NUM_OFFICIALAXA_L11_AREA, :NUM_RANGE])
amp_max = np.max(amp)
print(f"Max Value: {amp_max}")
intencity = 10*np.log10(amp**2)-10
# histgram plot
plt.figure(figsize=(16, 4))
plt.hist(intencity.flatten(), bins=100, range=(-30, 15), density=True)
plt.xlabel("Intensity [dB]")
plt.ylabel("Density")
plt.title("Intensity Histogram")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(PATH_OUTPUT, "intensity_histogram.png"), bbox_inches='tight', format='png', dpi=160)
# plt.show();
plt.clf();plt.close()


# ## compressed image
percentil_2 = np.percentile(intencity.flatten(), 2)
percentil_95 = np.percentile(intencity.flatten(), 95)
print(f"Percentile 2% >>> {percentil_2}, 95% >>> {percentil_95}")

plt.figure(figsize=(24, 16), facecolor='w', edgecolor='k', dpi=160)
plt.title(f'ALOS PALSAR Focus Intensity Image {CREDIT}', fontsize=20)
plt.imshow(intencity, vmax=percentil_95, vmin=percentil_2, aspect='auto')
plt.colorbar(shrink=0.6)
plt.tight_layout()
plt.savefig(os.path.join(PATH_OUTPUT, 'intensity.png'))
# plt.show();
plt.clf();plt.close()


# save image 
plt.imsave(os.path.join(PATH_OUTPUT, 'data_comp.png'), 
           np.abs(data_az[:, :NUM_RANGE]), cmap='gray', vmax=6)





