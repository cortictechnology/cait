FROM python:slim
RUN apt-get update && apt-get -y install \
    curl \
    wget \
    git \
    sudo \
    zip \
    unzip \
    libssl-dev \
    libncurses5-dev \
    libsqlite3-dev \
    libreadline-dev \
    zlib1g-dev
    
RUN mkdir -p /home/pi; \
    useradd -p raspberry pi; \
    usermod -a -G root pi; \
    chown pi:pi /home/pi; \
    echo "pi ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/pi
RUN wget https://www.python.org/ftp/python/3.5.8/Python-3.5.8.tar.xz; \
    tar xf Python-3.5.8.tar.xz; \
    cd Python-3.5.8; \
    ./configure; \
    make -j4; \
    make install

WORKDIR /home/pi
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; \
    python3.5 get-pip.py; \
    python3.5 -m pip install --upgrade pip setuptools wheel rpyc==3.3.1 paho-mqtt cython

USER pi
RUN sudo python3.5 -m pip install paho-mqtt; \
    sudo rm Python-3.5.8.tar.xz; \
    sudo rm -rf Python-3.5.8; \
    sudo apt-get clean; \
    sudo apt-get -y autoremove
USER root
