# 基本環境 GPU: NVIDIA TRX 3090, CUDA: 11.6.1, cuDNN: 8.3.2, PyTorch: 1.12.0a0+2c916ef
# リリースノート: https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel_22-03.html
FROM nvcr.io/nvidia/pytorch:22.03-py3

# 新しい世代の GPU 
## RTX 40x0
# https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-23-10.html
# FROM nvcr.io/nvidia/pytorch:23.10-py3
## RTX 50x0
# nvcr.io/nvidia/pytorch:25.01-py3
# FROM nvcr.io/nvidia/pytorch:25.01-py3
## 現状の最新
# https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html
# FROM nvcr.io/nvidia/pytorch:26.05-py3

# 基本設定
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN apt-get update --fix-missing && \
    apt-get install -y \
        gdal-bin \
        libgdal-dev \
        curl \
        screen \
        htop \
        zip \
        libopencv-dev

# conda env 作成
RUN conda create -n sar-book python=3.9 -y && \
    conda clean -a -y

# GDAL は pip(pyGdal)ではなく conda-forge からインストール
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate sar-book && \
    conda install -y -c conda-forge gdal && \
    conda clean -a -y"

# bash 起動時に自動で conda activate（conda 初期化も含める）
RUN echo 'source /opt/conda/etc/profile.d/conda.sh' >> ~/.bashrc && \
    echo 'conda activate sar-book' >> ~/.bashrc

# requirements インストール
COPY env/requirements.txt /tmp/requirements.txt
RUN /opt/conda/envs/sar-book/bin/pip install --upgrade pip && \
    /opt/conda/envs/sar-book/bin/pip install -r /tmp/requirements.txt

# 作業ディレクトリ
WORKDIR /work

# bash を entrypoint に（activate される）
CMD ["bash", "--login"]
