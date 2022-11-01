FROM quay.io/skopeo/stable:latest
RUN useradd -u 1001 mirrorsync
USER mirrorsync
VOLUME ["/var/spool/apt-mirror"]