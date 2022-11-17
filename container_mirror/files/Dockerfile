FROM alpine:3.17
RUN mkdir -p /mnt/repos/
RUN apk add --no-cache skopeo
RUN addgroup -S transferbuddy && adduser -S transferbuddy -u 1001 -G transferbuddy
RUN chown -R transferbuddy /mnt/repos
USER transferbuddy
VOLUME ["/mnt/repos"]
ENTRYPOINT ["/usr/bin/skopeo"]