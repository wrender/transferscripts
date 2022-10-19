FROM rockylinux:9.0
COPY files/entrypoint.sh /opt/entrypoint.sh
RUN dnf install -y yum-utils \
  && \
    rm -rf /etc/yum.repos.d/* \
  && \
    mkdir -p /mnt/repos \
  && \
    chmod u+x /opt/entrypoint.sh
COPY files/mirrors.repo /etc/yum.repos.d/mirrors.repo
VOLUME ["/mnt/repos"]
ENTRYPOINT ["/opt/entrypoint.sh"]
