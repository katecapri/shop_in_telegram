FROM postgres:13.3
RUN mkdir -p /docker-entrypoint-initdb.d
COPY db/init-db.sh /docker-entrypoint-initdb.d/init-db.sh