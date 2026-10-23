ARG RTL_IMAGE=shahanafarooqui/rtl:v0.15.15@sha256:fdf3c8dc5843eccd556e475265487b2be24478727cd160e51127ea65c2a3bbb6
FROM ${RTL_IMAGE} AS upstream

FROM upstream AS patched
ARG RTL_TAG=v0.15.15
ARG RTL_COMMIT=9afea82871c4f176b38ea31190d696344985a917
RUN apk add --no-cache git openssl
WORKDIR /build/RTL
RUN git clone --depth 1 -b "$RTL_TAG" https://github.com/Ride-The-Lightning/RTL.git . \
 && test "$(git rev-parse HEAD)" = "$RTL_COMMIT"
# Retain the official frontend; compile only the backend requiring the TLS source patch.
RUN cmp package.json /RTL/package.json && npm ci --legacy-peer-deps
COPY patches/rtl-lnd-tls-verification.patch /tmp/rtl-lnd-tls-verification.patch
RUN git apply --check /tmp/rtl-lnd-tls-verification.patch \
 && git apply /tmp/rtl-lnd-tls-verification.patch \
 && npm run buildbackend
RUN cp -a /RTL/frontend ./frontend && chown -R node:node /build/RTL
USER node
RUN npm run testbackend

FROM upstream
RUN test "$(node --version)" = v22.23.4 \
 && apk add --no-cache --upgrade 'ca-certificates>=20261020' 'ca-certificates-bundle>=20261020'
COPY --from=patched /build/RTL/backend /RTL/backend
COPY RTL-Config.json render-config.cjs entrypoint.sh /opt/dappnode/
RUN chmod 755 /opt/dappnode/entrypoint.sh
ENV CHANNEL_BACKUP_PATH=/RTL/backup/node-1
WORKDIR /RTL
EXPOSE 80
ENTRYPOINT ["/sbin/tini", "-g", "--", "/opt/dappnode/entrypoint.sh"]
