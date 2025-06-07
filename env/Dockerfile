FROM nvcr.io/nvidia/pytorch:22.03-py3

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

# conda init をして .bashrc に必要な初期化コードを追加
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda init bash"

# bash 起動時に自動で conda activate
RUN echo "conda activate sar-book" >> ~/.bashrc

# requirements インストール
COPY env/requirements.txt /tmp/requirements.txt
RUN /opt/conda/envs/sar-book/bin/pip install --upgrade pip && \
    /opt/conda/envs/sar-book/bin/pip install -r /tmp/requirements.txt

# 作業ディレクトリ
WORKDIR /work

# bash を entrypoint に（activate される）
CMD ["bash", "--login"]
