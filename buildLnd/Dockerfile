ARG LND_IMAGE=lightninglabs/lnd:v0.21.4-beta@sha256:04d06edcc0f6e99a5e797ea34959f330add222226f840cd86afbc31f8f29627d
FROM ${LND_IMAGE}
# Keep the official LND binaries and refresh system trust.
RUN apk add --no-cache --upgrade 'ca-certificates>=20261020' 'ca-certificates-bundle>=20261020'
COPY entrypoint.sh /opt/dappnode/entrypoint.sh
RUN chmod 755 /opt/dappnode/entrypoint.sh
EXPOSE 8080 9735 10009
ENTRYPOINT ["/opt/dappnode/entrypoint.sh"]
