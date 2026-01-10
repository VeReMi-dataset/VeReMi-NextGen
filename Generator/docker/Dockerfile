FROM ubuntu:22.04

LABEL org.opencontainers.image.source=https://github.com/vs-uulm/VeReMi-NextGen
LABEL description="Official VeReMi-NextGen Simulation Environment"

ENV DEBIAN_FRONTEND=noninteractive
ENV SUMO_HOME=/usr/share/sumo

RUN apt-get update && apt-get install -y \
    openjdk-17-jdk python3 python3-pip python3-dev python3-venv python-is-python3 \
    software-properties-common wget unzip build-essential gcc g++ bison flex perl \
    qtbase5-dev libqt5opengl5-dev libxml2-dev zlib1g-dev libwebkit2gtk-4.0-37 \
    ca-certificates libprotobuf-dev protobuf-compiler libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository -y ppa:sumo/stable && \
    apt-get update && \
    apt-get install -y sumo sumo-tools sumo-doc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mosaic
ARG MOSAIC_VERSION=25.2

RUN wget --quiet "https://www.dcaiti.tu-berlin.de/research/simulation/download/get/eclipse-mosaic-${MOSAIC_VERSION}.zip" -O mosaic.zip && \
    unzip -q mosaic.zip && \
    mv eclipse-mosaic-${MOSAIC_VERSION}/* . || mv mosaic/* . || true && \
    rm -rf eclipse-mosaic-${MOSAIC_VERSION} mosaic mosaic.zip

RUN cd bin/fed/omnetpp && \
    chmod +x omnet_installer.sh && \
    yes y | ./omnet_installer.sh --installation-type USER

WORKDIR /opt/mosaic
RUN mkdir -p /opt/mosaic/tmp /opt/mosaic/logs /opt/mosaic/output
RUN chmod -R 777 /opt/mosaic

ENV PATH="/opt/mosaic/fed/omnetpp/bin:${PATH}"
RUN rm -rf /opt/mosaic/scenarios/*

COPY entrypoint.sh /opt/mosaic/entrypoint.sh
RUN chmod +x /opt/mosaic/entrypoint.sh

ENTRYPOINT ["/opt/mosaic/entrypoint.sh"]
