FROM debian:bookworm

RUN apt update && apt install -y \
    git wget dpkg unzip axel\
    gcc zlib1g-dev\
    build-essential \
    libssl-dev \
    libffi-dev \
    # install python3
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-venv \
    # install openjdk-17
    openjdk-17-jdk \
    xserver-xorg xorg xvfb\
    cmake libboost-dev \
    libexpat1-dev  libbz2-dev \
    # imagemagick
    libpng-dev libjpeg-dev libtiff-dev imagemagick\
    # install QGIS 
    gnupg software-properties-common\
    && mkdir -m755 -p /etc/apt/keyrings \
    && wget -O /etc/apt/keyrings/qgis-archive-keyring.gpg https://download.qgis.org/downloads/qgis-archive-keyring.gpg \
    && echo 'Types: deb deb-src' >> /etc/apt/sources.list.d/qgis.sources \
    && echo 'URIs: https://qgis.org/debian' >> /etc/apt/sources.list.d/qgis.sources \
    && echo 'Suites: bookworm' >> /etc/apt/sources.list.d/qgis.sources \
    && echo 'Architectures: amd64' >> /etc/apt/sources.list.d/qgis.sources \
    && echo 'Components: main' >> /etc/apt/sources.list.d/qgis.sources \
    && echo 'Signed-By: /etc/apt/keyrings/qgis-archive-keyring.gpg' >> /etc/apt/sources.list.d/qgis.sources \
    && apt update \
    && apt install -y qgis qgis-plugin-grass\
    # install worldpainter
    && wget -O /tmp/worldpainter_2.21.0.deb https://www.worldpainter.net/files/worldpainter_2.21.0.deb \
    && dpkg -i /tmp/worldpainter_2.21.0.deb \
    && rm /tmp/worldpainter_2.21.0.deb \
    && mkdir -p /root/.local/share/worldpainter/ \
    ## change worldpainter config
    && sed -i 's/# -Xmx512m/-Xmx6G/g' /opt/worldpainter/wpscript.vmoptions \
    # install Minutor
    && wget -O /tmp/Minutor.Ubuntu-22.04.zip https://github.com/mrkite/minutor/releases/download/2.20.0/Minutor.Ubuntu-22.04.zip \
    && unzip /tmp/Minutor.Ubuntu-22.04.zip \
    && chmod +x minutor \
    && mv minutor /usr/bin/ \
    && rm /tmp/Minutor.Ubuntu-22.04.zip \
    # post cleanup
    && apt clean \
    # pip install osmium
    && pip install osmium pebble pyyaml --break-system-packages \
    && rm -rf /root/.cache/pip \
    && rm -rf /var/lib/apt/lists/* \
    # remove Imagemagick policy
    && rm /etc/ImageMagick-6/policy.xml \
    # setup work space
    && mkdir -p /workspace

COPY config /root/.local/share/worldpainter/config
COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /workspace

# run run.sh
CMD ["./run.sh"]