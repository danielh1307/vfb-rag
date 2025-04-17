FROM postgres:15

# Install build dependencies
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        git \
        postgresql-server-dev-15 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install

# Clean up
RUN apt-get remove -y build-essential git postgresql-server-dev-15 \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /pgvector 