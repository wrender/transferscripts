FROM ubuntu:20.04
COPY files/entrypoint.sh /opt/entrypoint.sh
RUN apt-get update -q \
  && \
    apt install -y -qq apt-mirror \
  && \
    touch /var/log/cron.log \
  && \
    chmod u+x /opt/entrypoint.sh
COPY files/ubuntu-mirror.list /etc/apt/mirror.list
VOLUME ["/var/spool/apt-mirror"]
ENTRYPOINT ["/opt/entrypoint.sh"]
