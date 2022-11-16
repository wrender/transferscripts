FROM rockylinux:9.0
RUN dnf install -y yum-utils wget \
  && \
    rm -rf /etc/yum.repos.d/* \
  && \
    mkdir -p /mnt/repos
RUN useradd -u 1001 -ms /bin/bash transferbuddy
USER transferbuddy
VOLUME ["/mnt/repos"]
ENTRYPOINT ["/bin/bash","/opt/rundnf.sh"]