FROM python:3.7-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y update && apt-get -y install \
    curl \
    wget \
    sudo \
    gcc \
    git \
    build-essential \
    cmake \
    pkg-config \
	gnupg

RUN echo "deb http://raspbian.raspberrypi.org/raspbian/ buster main contrib non-free rpi" >> /etc/apt/sources.list; \
	echo "deb-src http://archive.raspbian.org/raspbian/ buster main contrib non-free rpi" >> /etc/apt/sources.list; \
    echo "deb http://archive.raspberrypi.org/debian/ buster main ui" >> /etc/apt/sources.list.d/raspi.list; \
    echo "deb-src http://archive.raspberrypi.org/debian/ buster main ui" >> /etc/apt/sources.list.d/raspi.list; \
    wget -qO - http://archive.raspberrypi.org/debian/raspberrypi.gpg.key | apt-key add -; \
    wget http://archive.raspbian.org/raspbian.public.key -O - | apt-key add -; \
    apt-get -y update && apt-get -y upgrade

WORKDIR /root
RUN mkdir -p .config/pip; \
    echo "[global]" >> .config/pip/pip.conf; \
    echo "index-url=https://pypi.org/simple" >> .config/pip/pip.conf; \
    echo "extra-index-url=https://www.piwheels.org/simple" >> .config/pip/pip.conf; \
	mkdir -p /usr/share/man/man1

RUN apt-get -y update && apt-get -y install \
    libbz2-dev \
    libssl-dev \
    tk-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline6-dev \
    libdb5.3-dev \
    libgdbm-dev \
    libsqlite3-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    zlib1g-dev \
    libffi-dev \
    openjdk-8-jdk \
    libhdf5-dev \
    libc-ares-dev \
    libeigen3-dev \
    gfortran \
    python-dev \
    libgfortran5 \
    libatlas3-base \
    libatlas-base-dev \
    libopenblas-dev \
    libopenblas-base \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    openmpi-bin \
    libopenmpi-dev \
    python3-dev 

ENV VIRTUAL_ENV=/root/rasa_env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; \
    python get-pip.py

WORKDIR /root
RUN wget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py; \
    python get-poetry.py --version 1.0.8

WORKDIR /root
RUN git clone https://github.com/PINTO0309/Bazel_bin.git; \
    cd Bazel_bin/2.0.0/Raspbian_Debian_Buster_armhf/openjdk-8-jdk; \
    chmod a+x install.sh; \
    ./install.sh

RUN pip install keras_applications==1.0.8 --no-deps; \
    pip install keras_preprocessing==1.1.0 --no-deps; \
    pip install cython; \
    pip install h5py==2.10.0 pybind11 six wheel mock "jsonschema>=3.2,<3.3" pycparser

RUN wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-2.3.1-cp37-none-linux_armv7l_download.sh; \
    chmod a+x tensorflow-2.3.1-cp37-none-linux_armv7l_download.sh; \
    bash tensorflow-2.3.1-cp37-none-linux_armv7l_download.sh; \
    pip install tensorflow-2.3.1-cp37-none-linux_armv7l.whl; \
    rm tensorflow-2.3.1-cp37-none-linux_armv7l_download.sh; \
	rm tensorflow-2.3.1-cp37-none-linux_armv7l.whl; \
	pip install pip==20.0.2; \
	apt install rsync libpq-dev -y

# COPY tensorflow_addons-0.7.1-cp37-cp37m-linux_armv7l.whl /root
# WORKDIR /root
# RUN pip install tensorflow_addons-0.7.1-cp37-cp37m-linux_armv7l.whl; \
WORKDIR /root
RUN git clone https://github.com/tensorflow/addons.git
#     cd addons; \
#     echo "N" | ./configure.sh; \
#     bazel build --jobs=2 --enable_runfiles build_pip_pkg; \
#     bazel-bin/build_pip_pkg artifacts; \
#     pip install artifacts/tensorflow_addons-*.whl
# 	pip install protobuf==3.12.2

# WORKDIR /root
# RUN pip install scikit-build wheel==0.34.2 setuptools; \
# 	git clone https://github.com/RasaHQ/rasa.git; \
#     cd rasa; \
#     git checkout tags/1.10.2; \
# 	sed -i 's/version = "3.12.0"/version = "3.12.2"/g' poetry.lock

# WORKDIR /root/rasa
# RUN /bin/bash -c "source /root/.poetry/env && make install"

# WORKDIR /root
# RUN git clone https://github.com/explosion/spaCy; \
#     export BLIS_ARCH=generic; \
#     cd spaCy; \
#     pip install -r requirements.txt; \
#     python setup.py build_ext --inplace; \
#     pip install .

# WORKDIR /root
# RUN apt-get clean; \
#     apt-get -y autoremove; \
#     rm -rf Bazel_bin; \
#     rm tensorflow_addons-0.7.1-cp37-cp37m-linux_armv7l.whl; \
#     rm -rf spaCy; \
#     rm get-pip.py; \
#     rm get-poetry.py