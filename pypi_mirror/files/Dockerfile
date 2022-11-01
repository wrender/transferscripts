FROM pypa/bandersnatch
RUN mkdir -p /mnt/repos/
RUN useradd -u 1001 -ms /bin/bash mirrorsync
RUN chown -R mirrorsync /mnt/repos
RUN chown -R mirrorsync /bandersnatch
USER mirrorsync
VOLUME ["/mnt/repos"]
CMD ["bandersnatch","-c", "/conf/bandersnatch.conf","mirror"]