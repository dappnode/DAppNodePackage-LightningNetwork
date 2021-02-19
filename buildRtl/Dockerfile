ARG UPSTREAM_VERSION
FROM  shahanafarooqui/rtl:$UPSTREAM_VERSION

### DEFAULT ENTRYPOINT
#COPY ./RTL-Config.json /RTL
###

### OVERRIDE ENTRYPOINT
COPY ./entrypoint.sh /RTL
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/sbin/tini", "-g", "--", "/RTL/entrypoint.sh"]
###