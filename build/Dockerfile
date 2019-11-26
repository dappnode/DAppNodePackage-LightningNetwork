FROM node:10.16.0-alpine as build

ENV LND_VERSION "v0.8.1-beta"
ENV RTL_TAG "v0.5.4"

RUN apk add --no-cache wget ca-certificates \
 && wget https://github.com/lightningnetwork/lnd/releases/download/${LND_VERSION}/lnd-linux-amd64-${LND_VERSION}.tar.gz \
 && tar --strip-components 1 -xzf  lnd-linux-amd64-${LND_VERSION}.tar.gz -C /bin/ \
 && rm lnd-linux-amd64-${LND_VERSION}.tar.gz \
 && apk del wget ca-certificates

# Add build requirements
RUN apk add --no-cache \
    bash curl openssl supervisor git make g++

RUN git clone -b $RTL_TAG https://github.com/Ride-The-Lightning/RTL.git /rtl

WORKDIR /rtl

RUN npm install
RUN rm -rf ./node_modules/* &&  npm install --only=production && npm install @types/node

FROM alpine

WORKDIR /rtl

ENV CHANNEL_BACKUP_PATH /root/.lnd

# Add requirements
RUN apk add --no-cache supervisor bash curl nodejs openssl gettext

COPY --from=build /rtl /rtl
COPY --from=build /bin/lnd /bin/lnd
COPY --from=build /bin/lncli /bin/lncli

COPY src/scripts/start-lnd.sh /
COPY src/scripts/start-rtl.sh /rtl
COPY src/config/source_RTL.conf /rtl

RUN ln -s /root/.lnd /config

RUN mkdir -p /var/log/supervisor
COPY src/config/supervisord.conf /

# Expose lnd ports (server, rpc).
EXPOSE 9735 10009 80

CMD ["supervisord","-c","/supervisord.conf"]
