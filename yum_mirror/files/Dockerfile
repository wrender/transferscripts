FROM rockylinux:9.0
COPY entrypoint.sh /opt/entrypoint.sh
RUN dnf install -y yum-utils \
  && \
    rm -rf /etc/yum.repos.d/* \
  && \
    mkdir -p /mnt/repos \
  && \
    chmod u+x /opt/entrypoint.sh
RUN useradd -u 1001 -ms /bin/bash transferbuddy
RUN chown transferbuddy /opt/entrypoint.sh
USER transferbuddy
COPY yum-mirrors.repo /etc/yum.repos.d/mirrors.repo
VOLUME ["/mnt/repos"]
ENTRYPOINT ["/opt/entrypoint.sh"]