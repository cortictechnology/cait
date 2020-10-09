FROM ubuntu

# install base tools
RUN apt-get update && apt-get -y upgrade && apt-get -y install \
	curl \
	tar \
	wget \
	sudo \
	xz-utils \
	gcc \
	make \
	libatomic-ops-dev \
	libbz2-dev libssl-dev \
	build-essential \
	cmake \
	unzip \
	pkg-config \
	zlib1g \
	zlib1g-dev

# install python 3.6.8
WORKDIR /root
RUN wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tar.xz; \
tar -xvf Python-3.6.8.tar.xz
WORKDIR /root/Python-3.6.8
RUN ./configure; \
make -j4; \
make install; \
python3.6 -m pip install --upgrade pip setuptools wheel

# install tensorflow 1.14.0
RUN apt-get install python3.6-dev libhdf5-dev -y; \
touch /etc/pip.conf; \
echo '[global]\nextra-index-url=https://www.piwheels.org/simple' >> /etc/pip.conf; \
python3.6 -m pip install tensorflow==1.14.0

# install opencv
RUN apt-get -y install \
	libatlas3-base \
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
	libgtk-3-dev \
	libcanberra-gtk* \
	libqtgui4 \
	libqtwebkit4 \
	libqt4-test \
	python3-pyqt5 \
	git
WORKDIR /root
RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.0.0.zip; \
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.0.0.zip; \
unzip opencv.zip; \
unzip opencv_contrib.zip; \
mv opencv-4.0.0 opencv; \
mv opencv_contrib-4.0.0 opencv_contrib; \
rm opencv.zip; \
rm opencv_contrib.zip
WORKDIR /root/opencv
RUN mkdir build
WORKDIR /root/opencv/build
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..; \
make -j4; \
make install; \
ldconfig
WORKDIR /usr/local/lib/python3.6/site-packages/
RUN sudo ln -s /usr/local/python/cv2/python-3.6/cv2.cpython-36m-arm-linux-gnueabihf.so cv2.so; \
rm -rf ~/opencv*; \
rm -rf ~/Python*

# install rasa
WORKDIR /root
RUN git clone https://github.com/explosion/spaCy; \
git clone https://github.com/tensorflow/tensor2tensor; \
git clone https://github.com/google/dopamine.git; \
wget https://github.com/RasaHQ/rasa/archive/1.4.3.zip && unzip 1.4.3.zip
WORKDIR /root/spaCy
RUN export BLIS_ARCH=generic; \
python3.6 -m pip install -r requirements.txt; \
python3.6 setup.py build_ext --inplace; \
python3.6 -m pip install .; \
pip install picamera
WORKDIR /root/dopamine
RUN sed -i '/opencv-python/d' setup.py; \
sed -i 's/gym >= 0.10.5/gym == 0.15.3/g' setup.py; \
cat setup.py; \
python3.6 -m pip install .; \
rm ~/1.4.3.zip
WORKDIR /root/tensor2tensor
RUN apt-get -y install libpq-dev libffi-dev locales; \
sed -i '/opencv-python/d' setup.py; \
sed -i '/dopamine-rl/d' setup.py; \
sed -i 's/gym/gym == 0.15.3/g' setup.py; \
python3.6 -m pip install .; \
python3.6 -m pip install psycopg2
WORKDIR /root/rasa-1.4.3
RUN sed -i '/tensor2tensor/d' setup.py; \
sed -i '/tensor2tensor/d' requirements.txt

RUN python3.6 -m pip install -r requirements.txt; \
python3.6 -m pip install . ; \
echo ""; \
echo ""; \
echo "------------------------------------------------------------"; \
echo "Congratulations! Rasa is now installed on your Raspberry Pi."; \
echo "To test rasa out, run python3.6 -m rasa init and start "; \
echo "creating your bot!"; \
python3 -m spacy download en_core_web_md; \
python3 -m spacy link en_core_web_md en

#install mqtt
RUN pip install paho-mqtt
ENV PYTHONIOENCODING='utf8'

# clean up
WORKDIR /root
RUN rm -rf dopamine; \
rm -rf spaCy; \
rm -rf tensor2tensor; \
rm -rf rasa-1.4.3; \
rm -rf .cache; \
apt-get -y clean; \
apt-get -y autoremove 
