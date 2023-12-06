# world-generator

The World Generator inspired by [Minecraft Earth Map](https://earth.motfe.net/) but runs in parallel.

## Requirements

Ubuntu 22.04 LTS, run the following command to install the dependencies. Later Docker image will be provided.

```bash
sudo apt install -y \
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
    && sudo mkdir -m755 -p /etc/apt/keyrings \
    && sudo wget -O /etc/apt/keyrings/qgis-archive-keyring.gpg https://download.qgis.org/downloads/qgis-archive-keyring.gpg \
    && sudo echo 'Types: deb deb-src' >> /etc/apt/sources.list.d/qgis.sources \
    && sudo echo 'URIs: https://qgis.org/debian' >> /etc/apt/sources.list.d/qgis.sources \
    && sudo echo 'Suites: bookworm' >> /etc/apt/sources.list.d/qgis.sources \
    && sudo echo 'Architectures: amd64' >> /etc/apt/sources.list.d/qgis.sources \
    && sudo echo 'Components: main' >> /etc/apt/sources.list.d/qgis.sources \
    && sudo echo 'Signed-By: /etc/apt/keyrings/qgis-archive-keyring.gpg' >> /etc/apt/sources.list.d/qgis.sources \
    && sudo apt update \
    && sudo apt install -y qgis qgis-plugin-grass\
    # install worldpainter
    && wget -O /tmp/worldpainter_2.21.0.deb https://www.worldpainter.net/files/worldpainter_2.21.0.deb \
    && sudo dpkg -i /tmp/worldpainter_2.21.0.deb \
    && rm /tmp/worldpainter_2.21.0.deb \
    && mkdir -p /root/.local/share/worldpainter/ \
    # install Minutor
    && wget -O /tmp/Minutor.Ubuntu-22.04.zip https://github.com/mrkite/minutor/releases/download/2.20.0/Minutor.Ubuntu-22.04.zip \
    && unzip /tmp/Minutor.Ubuntu-22.04.zip \
    && chmod +x minutor \
    && mv minutor /usr/bin/ \
    && rm /tmp/Minutor.Ubuntu-22.04.zip \
    # pip install osmium
    && pip install osmium --break-system-packages \
```

Download the project from release. Then copy config.json.example to config.json and edit it.
**Note: Not all the features in Minecraft Earth Map are implemented.** Welcome to contribute.

```bash
cp config.json.example config.json
gedit config.json
```

Edit the worldpainter vmoptions file, change the memory size to `-Xmx6G` or more. Copy the following content to the file.

```text
# Enter one VM parameter per line
# For example, to adjust the maximum memory usage to 512 MB, uncomment the following line:
-Xmx6G
# To include another file, uncomment the following line:
# -include-options [path to other .vmoption file]
```

```bash
sudo gedit /opt/worldpainter/wpscript.vmoptions
```

Change the policy of imagemagick, enable processing of images. Copy the following content to the file.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policymap [
  <!ELEMENT policymap (policy)*>
  <!ATTLIST policymap xmlns CDATA #FIXED ''>
  <!ELEMENT policy EMPTY>
  <!ATTLIST policy xmlns CDATA #FIXED '' domain NMTOKEN #REQUIRED
    name NMTOKEN #IMPLIED pattern CDATA #IMPLIED rights NMTOKEN #IMPLIED
    stealth NMTOKEN #IMPLIED value CDATA #IMPLIED>
]>
<policymap>
  <policy domain="resource" name="memory" value="40GiB"/>
  <policy domain="resource" name="map" value="40GiB"/>
  <policy domain="resource" name="width" value="16KP"/>
  <policy domain="resource" name="height" value="16KP"/>
  <policy domain="resource" name="area" value="128MP"/>
  <policy domain="resource" name="disk" value="2000GiB"/>
  <policy domain="path" rights="read|write" pattern="@*"/>
  <policy domain="coder" rights="read|write" pattern="PS" />
  <policy domain="coder" rights="read|write" pattern="PS2" />
  <policy domain="coder" rights="read|write" pattern="PS3" />
  <policy domain="coder" rights="read|write" pattern="EPS" />
  <policy domain="coder" rights="read|write" pattern="PDF" />
  <policy domain="coder" rights="read|write" pattern="XPS" />
  <policy domain="coder" rights="read|write" pattern="@*" />
</policymap>
```

```bash
sudo gedit /etc/ImageMagick-6/policy.xml
```

## Run it

```bash
xvfb-run python3 main.py > err.log
```

Log files in `generator.log` and `err.log`.
