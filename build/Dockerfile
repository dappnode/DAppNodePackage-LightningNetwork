FROM node:8.15.0-alpine as build

ENV LND_VERSION "v0.5.2-beta"
ENV LNCLI_WEB_TAG "master"

RUN apk add --no-cache wget ca-certificates \
 && wget https://github.com/lightningnetwork/lnd/releases/download/${LND_VERSION}/lnd-linux-amd64-${LND_VERSION}.tar.gz \
 && tar --strip-components 1 -xzf  lnd-linux-amd64-${LND_VERSION}.tar.gz -C /bin/ \
 && rm lnd-linux-amd64-${LND_VERSION}.tar.gz \
 && apk del wget ca-certificates

# Add requirements
RUN apk add --no-cache \
    bash curl openssl supervisor git make g++

RUN git clone -b $LNCLI_WEB_TAG https://github.com/mably/lncli-web.git /lncli-web

WORKDIR /lncli-web

RUN npm install &&  ./node_modules/.bin/gulp bundles
RUN rm -rf ./node_modules/* &&  npm install --only=production

FROM alpine

WORKDIR /lncli-web

# Add requirements
RUN apk add --no-cache supervisor bash curl nodejs openssl

COPY --from=build /lncli-web /lncli-web
COPY --from=build /bin/lnd /bin/lnd

COPY src/scripts/start-lnd.sh /
COPY src/scripts/start-lncli-web.sh /lncli-web
COPY src/scripts/wait-for-it.sh /lncli-web

RUN ln -s /root/.lnd /config

RUN mkdir -p /var/log/supervisor
COPY src/config/supervisord.conf /

# Expose lnd ports (server, rpc).
EXPOSE 9735 10009 80

CMD ["supervisord","-c","/supervisord.conf"]