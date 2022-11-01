FROM rockylinux:9.0
RUN dnf install -y yum-utils \
  && \
    rm -rf /etc/yum.repos.d/* \
  && \
    mkdir -p /mnt/repos
RUN useradd -u 1001 -ms /bin/bash mirrorsync
USER mirrorsync
VOLUME ["/mnt/repos"]
ENTRYPOINT ["/bin/bash","/opt/rundnf.sh"]