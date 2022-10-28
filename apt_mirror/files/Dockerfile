FROM ubuntu:20.04
COPY entrypoint.sh /opt/entrypoint.sh
RUN apt-get update -q \
  && \
    apt install -y -qq apt-mirror \
  && \
    touch /var/log/cron.log \
  && \
    chmod u+x /opt/entrypoint.sh
RUN useradd -u 1001 -ms /bin/bash transferbuddy
RUN chown transferbuddy /opt/entrypoint.sh
USER transferbuddy
COPY ubuntu-mirror.list /etc/apt/mirror.list
VOLUME ["/var/spool/apt-mirror"]
ENTRYPOINT ["/opt/entrypoint.sh"]