ARG UPSTREAM_VERSION
FROM lightninglabs/lnd:$UPSTREAM_VERSION

EXPOSE 8080 9735 10009

### DEFAULT ENTRYPOINT
#COPY ./lnd.conf /root/.lnd/
###

### OVERRIDE ENTRYPOINT
COPY ./entrypoint.sh /root
RUN chmod +x /root/entrypoint.sh
ENTRYPOINT [ "/root/entrypoint.sh" ]
###