FROM alpine

ENV VERSION "0.5-beta"

RUN apk add --no-cache wget ca-certificates \
 && wget https://github.com/lightningnetwork/lnd/releases/download/v${VERSION}/lnd-linux-amd64-v${VERSION}.tar.gz \
 && tar --strip-components 1 -xzf  lnd-linux-amd64-v${VERSION}.tar.gz -C /bin/ \
 && rm lnd-linux-amd64-v${VERSION}.tar.gz \
 && apk del wget ca-certificates

# Expose lnd ports (server, rpc).
EXPOSE 9735 10009

# Add bash.
RUN apk add --no-cache \
    bash

# Copy the entrypoint script.
COPY "start-lnd.sh" .
RUN chmod +x start-lnd.sh

ENTRYPOINT ["./start-lnd.sh"]