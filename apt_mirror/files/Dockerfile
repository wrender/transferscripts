FROM ubuntu:20.04
RUN apt-get update -q \
  && \
    apt install -y -qq apt-mirror \
  && \
    touch /var/log/cron.log
RUN useradd -u 1001 -ms /bin/bash transferbuddy
USER transferbuddy
VOLUME ["/var/spool/apt-mirror"]
CMD ["apt-mirror"]