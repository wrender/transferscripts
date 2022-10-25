FROM ubuntu:20.04
COPY entrypoint.sh /opt/entrypoint.sh
RUN apt-get update -q \
  && \
    apt install -y -qq apt-mirror \
  && \
    touch /var/log/cron.log \
  && \
    chmod u+x /opt/entrypoint.sh
RUN useradd -u 1000 -ms /bin/bash wrender
RUN chown wrender /opt/entrypoint.sh
USER wrender
COPY ubuntu-mirror.list /etc/apt/mirror.list
VOLUME ["/var/spool/apt-mirror"]
ENTRYPOINT ["/opt/entrypoint.sh"]