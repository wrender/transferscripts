FROM pypa/bandersnatch
RUN mkdir -p /mnt/repos/
RUN useradd -u 1001 -ms /bin/bash transferbuddy
RUN chown -R transferbuddy /mnt/repos
RUN chown -R transferbuddy /bandersnatch
USER transferbuddy
VOLUME ["/mnt/repos"]
CMD ["bandersnatch","-c", "/conf/bandersnatch.conf","mirror"]