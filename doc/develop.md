## ⚙️ 環境構築

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

MMシリーズは ハードウエアに強く依存します。そのため、基本的には、ハードウェアに適したライブラリの環境構築手順に従って構築してください。

ここでは、Linux での Nvidia GPU CUDA 11.5 での環境構築例をご紹介します。

#### mmdetection

![MMDetection Logo](https://raw.githubusercontent.com/open-mmlab/mmdetection/main/resources/mmdet-logo.png)

- Github: https://github.com/open-mmlab/mmdetection
- 公式のインストールガイド: https://mmdetection.readthedocs.io/en/latest/get_started.html


```shell

pip install -U openmim
# cuda 11.5
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116

mim install "mmengine>=0.7.0"
mim install "mmcv==2.0.0rc4"

# mmdetection
git clone https://github.com/open-mmlab/mmdetection.git

pip install -e ./mmdetection/
```

#### mmrotate

![MMRotate Logo](https://raw.githubusercontent.com/open-mmlab/mmrotate/main/resources/mmrotate-logo.png)

- Github: https://github.com/open-mmlab/mmrotate
- 公式のインストールガイド: https://github.com/open-mmlab/mmrotate/blob/main/docs/en/get_started.md

```shell
pip install -U openmim
# cuda 11.5
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116

mim install "mmcv-full==1.7.0"
mim install "mmdet==2.28.0"

# mmrotate
git clone https://github.com/open-mmlab/mmrotate.git 
pip install -r ./mmrotate/requirements/build.txt
pip install -v -e ./mmrotate
pip install numpy==1.26.4

# other library
pip install jupyterlab numpy tqdm matplotlib future tensorboard
```

#### Torch

![PyTorch](https://raw.githubusercontent.com/pytorch/pytorch/main/docs/source/_static/img/pytorch-logo-dark.png)

- Github: https://github.com/pytorch/pytorch
- 公式インストールガイド: https://pytorch.org/

PyTorch の CUDA のバージョン調整や過去バージョンを適用させる場合は[こちら]( https://pytorch.org/get-started/previous-versions/)の一覧から探すことが可能です。



## 動作確認環境

| マシン概要   | OS               | メモリ | CPU                 | ストレージ | 備考                          |
| ------------ | ---------------- | ------ | ------------------- | ---------- | ----------------------------- |
| Mac Book Air | OSX              | 16GB   | アップルシリコン M4 | 1T         | ALOS-2 干渉非動作(メモリ不足) |
| Mac Book Pro | OSX              | 36GB   | アップルシリコン M3 | 1T         | ALOS-2 干渉非動作(メモリ不足) |
| Linux BTO    | Ubuntu 22.04 LTS | 128GB  | AMP 16 Core         | 2T         | ----                          |
| Linux Cloud  | Amazon Linux     | 384GB  | ----                | 2T         | ----                          |
| 佐藤さんPC   | Windows          | GB     | ----                | T          | `確認中`                      |


## 推奨環境
| マシン概要 | OS       | メモリ | CPU        | ストレージ | 備考                   |
| ---------- | -------- | ------ | ---------- | ---------- | ---------------------- |
| ----       | 特になし | 32GB   | 8 Core CPU | 512GB      | ALOS-2干渉は考慮しない |
