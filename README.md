# sar-python-book

# 書影

## 書籍のリンク

## 書籍紹介記事




# コードと章の対応

| 章               | 節             | 内容              | ノートブックファイル                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------- | ------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 第1章 SARの基礎と観測原理 |    |   |   |
|                 | 合成開口          | 合成開口の基本         | [1\_1\_3\_impulse\_response.ipynb](./src/1_1_3_impulse_response.ipynb), [1\_1\_6\_migration.ipynb](./src/1_1_6_migration.ipynb), [1\_1\_7\_999\_synthetic\_aperture.ipynb](./src/1_1_7_999_synthetic_aperture.ipynb), [1\_1\_7\_focus.ipynb](./src/1_1_7_focus.ipynb) |
|                 | 強度画像          | マルチルッキングなど      | [1\_3\_3\_multilooking.ipynb](./src/1_3_3_multilooking.ipynb)|
|                 | レーダー特有の現象     | アンビギュイティ、RFI など | [1\_3\_7\_ambiguity\_azimuth.ipynb](./src/1_3_7_ambiguity_azimuth.ipynb), [1\_3\_7\_ambiguity\_range.ipynb](./src/1_3_7_ambiguity_range.ipynb), [1\_3\_9\_radio\_frequency\_interference.ipynb](./src/1_3_9_radio_frequency_interference.ipynb) |
|                 | SARの性能        | 偏波・ビーム・軌道       | [1\_3\_1\_polarimetry.ipynb](./src/1_3_1_polarimetry.ipynb), [1\_3\_2\_antena\_pattarn.ipynb](./src/1_3_2_antena_pattarn.ipynb), [1\_3\_2\_beam.ipynb](./src/1_3_2_beam.ipynb), [1\_3\_2\_orbit.ipynb](./src/1_3_2_orbit.ipynb)  |
|                 | 干渉SAR         | 干渉処理全般          | [1\_5\_1-2-3-5-6-7\_insar.ipynb](./src/1_5_1-2-3-5-6-7_insar.ipynb), [1\_5\_3\_coregistolation.ipynb](./src/1_5_3_coregistolation.ipynb), [1\_5\_4\_wrap\_phase.ipynb](./src/1_5_4_wrap_phase.ipynb), [1\_5\_6\_insar\_2pass.ipynb](./src/1_5_6_insar_2pass.ipynb), [1\_5\_9\_baseline.ipynb](./src/1_5_9_baseline.ipynb), [1\_5\_999\_insar\_topo.ipynb](./src/1_5_999_insar_topo.ipynb) |
|                 | 合成開口の応用       | 高度なSAR処理        | [1\_6\_1\_chirp\_scaling.ipynb](./src/1_6_1_chirp_scaling.ipynb), [1\_6\_1\_stolt\_interpolation.ipynb](./src/1_6_1_stolt_interpolation.ipynb), [1\_6\_2\_speckle\_noise.ipynb](./src/1_6_2_speckle_noise.ipynb), [1\_6\_2\_subaperture\_capella\_eiffel.ipynb](./src/1_6_2_subaperture_capella_eiffel.ipynb), [1\_6\_2\_subaperture\_umbra\_haneda.ipynb](./src/1_6_2_subaperture_umbra_haneda.ipynb), [1\_6\_3\_moving\_target.ipynb](./src/1_6_3_moving_target.ipynb), [1\_6\_999\_cphd.ipynb](./src/1_6_999_cphd.ipynb) |
| 第2章 SARデータの解析準備 |               |                 ||
|                 | SARデータの取得と可視化 | 基本的な可視化と取得      | [2\_2\_sar\_georeference.ipynb](./src/2_2_sar_georeference.ipynb) |
|    | 地理空間データの処理    | オルソ補正など         | [2\_2\_sar\_georeference.ipynb](./src/2_2_sar_georeference.ipynb) |
| 第3章 SARデータの解析   |               |                 | |
|                 | 森林・農業         | セグメンテーション・時系列   | [3\_2\_forest.ipynb](./src/3_2_forest.ipynb), [3\_3\_2-3\_crop\_paz-s2\_time-seriess.ipynb](./src/3_3_2-3_crop_paz-s2_time-seriess.ipynb), [3\_3\_2\_999\_crop\_paz.ipynb](./src/3_3_2_999_crop_paz.ipynb), [3\_3\_2\_999\_crop\_paz\_time-seriese.ipynb](./src/3_3_2_999_crop_paz_time-seriese.ipynb), [3\_3\_3\_999\_crop\_sentinel-2.ipynb](./src/3_3_3_999_crop_sentinel-2.ipynb), [3\_3\_4\_model.ipynb](./src/3_3_4_model.ipynb)                                                                                      |
|                 | 浸水・洪水         | 統計的処理           | [3\_1\_2\_simple\_thresholding.ipynb](./src/3_1_2_simple_thresholding.ipynb), [3\_1\_3\_local\_thresholding.ipynb](./src/3_1_3_local_thresholding.ipynb), [3\_1\_4\_s1\_flood\_extraction.ipynb](./src/3_1_4_s1_flood_extraction.ipynb)|
|                 | 地震            | 干渉解析            | [3\_4\_4\_insar\_higashinihon.ipynb](./src/3_4_4_insar_higashinihon.ipynb), [3\_4\_5\_insar\_alos2.ipynb](./src/3_4_5_insar_alos2.ipynb), [3\_4\_5\_pixeloffset.ipynb](./src/3_4_5_pixeloffset.ipynb), [3\_4\_6\_2.5d.ipynb](./src/3_4_6_2.5d.ipynb)  |
|                 | 船舶            | 検知と信号処理         | [3\_5\_1\_ship\_signal\_distribution.ipynb](./src/3_5_1_ship_signal_distribution.ipynb), [3\_5\_2\_cfar.ipynb](./src/3_5_2_cfar.ipynb), [3\_5\_2\_ssdd.ipynb](./src/3_5_2_ssdd.ipynb), [3\_5\_3\_mmrotate.ipynb](./src/3_5_3_mmrotate.ipynb)  | ー |
| 第4章 SARの現在と今後   |               |                 |  |
|                 | SARプロバイダー     | ー               | *(該当コードなし)* |
|                 | 将来の展開         | ー               | *(該当コードなし)* |
| 付録              |               |                 |  |
|                 | フーリエ変換と相関処理   | 数学的背景           | [Appendix\_Fourier\_Transform\_ Correlation\_ Processing.ipynb](./src/Appendix_Fourier_Transform_%20Correlation_%20Processing.ipynb)  |




## 環境構築

### 方法 1.

Python環境管理ツール[Anaconda](https://www.anaconda.com/download) を 使用する場合

Python Version は 3.9 以上が必要
```shell
# 仮想環境作成
conda create -n sar-book python=3.10

# 仮想環境適用
conda activate sar-book

# Gdal環境
conda install -c conda-forge gdal

# 基礎環境構築
pip install -r env/requirements.txt
```

### 方法 2.

[Docker](https://www.docker.com/ja-jp/)を使用した環境構築方法

#### Image Build
```shell
docker build -t sar-book:v1.0 -f env/Dockerfile .
```

#### Run Container

GPU 利用の場合

```shell
docker run -it --gpus all --ipc host --rm  --runtime=nvidia \
    -v $(pwd):/work/ \
    --name sar-book-container sar-book:v1.0 /bin/bash
```

GPU Driver の認識確認方法と例

```log
docker run -it --gpus all --ipc host --rm  --runtime=nvidia     -v $(pwd):/work/     --name sar-book-container sar-book:v1.0 /bin/bash

=============
== PyTorch ==
=============

NVIDIA Release 22.03 (build 33569136)
PyTorch Version 1.12.0a0+2c916ef

Container image Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Copyright (c) 2014-2022 Facebook Inc.
Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
Copyright (c) 2012-2014 Deepmind Technologies    (Koray Kavukcuoglu)
Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
Copyright (c) 2011-2013 NYU                      (Clement Farabet)
Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
Copyright (c) 2006      Idiap Research Institute (Samy Bengio)
Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)
Copyright (c) 2015      Google Inc.
Copyright (c) 2015      Yangqing Jia
Copyright (c) 2013-2016 The Caffe contributors
All rights reserved.

Various files include modifications (c) NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

```

起動後にエラーが出ない状態で、`nvidia-smi` を実行して以下のように CUDA が認識していること

```log
(sar-book) root@d42bff2a8fa4:/work# nvidia-smi
Sat May 17 19:59:37 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.133.07             Driver Version: 570.133.07     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3090        Off |   00000000:01:00.0  On |                  N/A |
|  0%   54C    P8             32W /  350W |     159MiB /  24576MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
+-----------------------------------------------------------------------------------------+
```


CPU 利用の場合

```shell
docker run -it --ipc host --rm \
    -v $(pwd):/work/ \
    --name sar-book-container sar-book:v1.0 /bin/bash
```

VSCode の拡張機能で [Dev Containar](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) と [Jupyter Notebook](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) 機能を追加して仮想環境内で操作することをおすすめします。

### 環境確認方法

確認用ファイル

```shell
python -V
# Python 3.9.22
python tests/test.py 
```

出力結果
```log
Python version: 3.9.22 | packaged by conda-forge | (main, Apr 14 2025, 23:35:59) 
[GCC 13.3.0]
Numpy version: 2.0.2
Tifffile version: 2024.8.30
OpenCV version: 4.11.0
Kornia version: 0.8.1
Seaborn version: 0.13.2
Rasterio version: 1.4.3
Joblib version: 1.5.0
Matplotlib version: 3.9.4
Torch version: 2.7.0+cu126
GDAL version: 3.0.4
```

### MMシリーズ環境構築


## 動作環境

TODO 動作確認環境の記載
- Mac Book Air M4 16GB
- Linux Ubuntu 22.04 LTS 64GB 

推奨環境
8 Core CPU
32GB Memory
1TB Storage
GPU 16GB