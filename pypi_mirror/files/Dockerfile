FROM pypa/bandersnatch
RUN mkdir -p /mnt/repos/
RUN useradd -u 1001 -ms /bin/bash transferbuddy
RUN chown -R transferbuddy /mnt/repos
USER transferbuddy
COPY bandersnatch.conf /conf/bandersnatch.conf
VOLUME ["/mnt/repos"]