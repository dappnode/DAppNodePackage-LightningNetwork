FROM node:alpine

ENV LND_VERSION "0.5-beta"
ENV LNCLI_WEB_TAG "master"

RUN apk add --no-cache wget ca-certificates \
 && wget https://github.com/lightningnetwork/lnd/releases/download/v${LND_VERSION}/lnd-linux-amd64-v${LND_VERSION}.tar.gz \
 && tar --strip-components 1 -xzf  lnd-linux-amd64-v${LND_VERSION}.tar.gz -C /bin/ \
 && rm lnd-linux-amd64-v${LND_VERSION}.tar.gz \
 && apk del wget ca-certificates

# Expose lnd ports (server, rpc).
EXPOSE 9735 10009 80

# Add requirements
RUN apk add --no-cache \
    bash curl openssl supervisor git

COPY "start-lnd.sh" .
RUN chmod +x start-lnd.sh

RUN git clone -b $LNCLI_WEB_TAG https://github.com/mably/lncli-web.git /lncli-web

WORKDIR /lncli-web

RUN npm install \
&&  ./node_modules/.bin/gulp bundles

RUN ln -s /root/.lnd /config

COPY "start-lncli-web.sh" .
COPY "wait-for-it.sh" .
RUN chmod +x start-lncli-web.sh
RUN chmod +x wait-for-it.sh

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf .

CMD ["supervisord"]
