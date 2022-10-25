FROM rockylinux:9.0
COPY entrypoint.sh /opt/entrypoint.sh
RUN dnf install -y yum-utils \
  && \
    rm -rf /etc/yum.repos.d/* \
  && \
    mkdir -p /mnt/repos \
  && \
    chmod u+x /opt/entrypoint.sh
RUN useradd -u 1000 -ms /bin/bash wrender
RUN chown wrender /opt/entrypoint.sh
USER wrender
COPY yum-mirrors.repo /etc/yum.repos.d/mirrors.repo
VOLUME ["/mnt/repos"]
ENTRYPOINT ["/opt/entrypoint.sh"]