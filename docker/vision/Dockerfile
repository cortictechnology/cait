FROM python:slim
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y update && apt-get -y install \
    curl \
    wget \
    sudo 

WORKDIR /root

RUN mkdir -p .config/pip; \
    echo "[global]" >> .config/pip/pip.conf; \
    echo "index-url=https://pypi.org/simple" >> .config/pip/pip.conf; \
    echo "extra-index-url=https://www.piwheels.org/simple" >> .config/pip/pip.conf; 

RUN apt-get -y update && apt-get -y install \
    libatlas3-base \
    build-essential \
    cmake \
    pkg-config \
    libatlas-base-dev \
    gfortran \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    ffmpeg \
    python3-pyqt5 \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libatomic-ops-dev \
    lsb-release \
    git 

RUN pip3 install picamera; \
    pip3 install numpy

WORKDIR  /root 
RUN apt-get -y update && apt-get -y install \
    zip \
    unzip 

RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.1.2.zip; \
    wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.1.2.zip; \
    unzip opencv.zip; \
    unzip opencv_contrib.zip; \
    rm opencv*.zip; \
    mv opencv-4.1.2 opencv; \
    mv opencv_contrib-4.1.2 opencv_contrib

WORKDIR /root/opencv
RUN mkdir build
WORKDIR /root/opencv/build

RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D CMAKE_SHARED_LINKER_FLAGS=-latomic \
    -D BUILD_EXAMPLES=OFF ..; \
    make -j4; \
    make install; \
    ldconfig

WORKDIR /root 
RUN wget https://dl.bintray.com/boostorg/release/1.71.0/source/boost_1_71_0.tar.bz2; \
    tar --bzip2 -xf boost_1_71_0.tar.bz2
    
WORKDIR /root/boost_1_71_0 
RUN ./bootstrap.sh --with-python=$(which python3) --with-libraries=filesystem,python; \
    ./b2 install

WORKDIR /root
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - 

RUN apt-get -y update && apt-get -y install \
    python3-edgetpu \
    libedgetpu1-std 

RUN git clone https://github.com/google-coral/edgetpu.git
WORKDIR /root/edgetpu
RUN yes | scripts/runtime/install.sh

RUN pip3 install paho-mqtt; \
    pip3 install ws4py; \
    pip3 install Pillow

WORKDIR /root
RUN apt-get -y install kmod
RUN apt-get clean; \
    apt-get -y autoremove; \
    rm -rf opencv; \
    rm -rf boost_1_71_0; \
    rm -rf edgetpu; \
    rm *.bz2
