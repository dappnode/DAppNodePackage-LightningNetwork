FROM node:alpine

ENV VERSION "0.5-beta"

RUN apk add --no-cache wget ca-certificates \
 && wget https://github.com/lightningnetwork/lnd/releases/download/v${VERSION}/lnd-linux-amd64-v${VERSION}.tar.gz \
 && tar --strip-components 1 -xzf  lnd-linux-amd64-v${VERSION}.tar.gz -C /bin/ \
 && rm lnd-linux-amd64-v${VERSION}.tar.gz \
 && apk del wget ca-certificates

# Expose lnd ports (server, rpc).
EXPOSE 9735 10009 8280

# Add requirements
RUN apk add --no-cache \
    bash curl openssl supervisor

COPY "start-lnd.sh" .
RUN chmod +x start-lnd.sh

COPY lncli-web/ /lncli-web

WORKDIR /lncli-web

RUN npm install \
&&  ./node_modules/.bin/gulp bundles

RUN ln -s /root/.lnd /config

COPY "start-lncli-web.sh" .
RUN chmod +x start-lncli-web.sh

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf .

CMD ["supervisord"]
