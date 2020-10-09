FROM python:slim
RUN apt-get update && apt-get -y install \
    curl \
    wget \
    git \
    sudo \
    zip \
    unzip
RUN mkdir -p /home/pi; \
    useradd -p raspberry pi; \
    usermod -a -G root pi; \
    chown pi:pi /home/pi; \
    echo "pi ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER pi
WORKDIR /home/pi
RUN curl -kL dexterindustries.com/update_brickpi3 | bash; \
    sudo pip3 install paho-mqtt; \
    sudo apt-get clean; \
    sudo apt-get -y autoremove
USER root
