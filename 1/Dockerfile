FROM ubuntu:22.04

# Install dependencies with cleanup
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    python3 \
    python3-pip \
    openjdk-11-jdk \
    gnupg \
    && wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - \
    && echo 'deb https://debian.neo4j.com stable 4.4' > /etc/apt/sources.list.d/neo4j.list \
    && apt-get update \
    && apt-get install -y neo4j=1:4.4.23 \
    && pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir neo4j pandas pyarrow requests\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure Neo4j
RUN echo "dbms.security.procedures.unrestricted=gds.*" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.procedures.whitelist=gds.*" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.directories.import=/var/lib/neo4j/import" >> /etc/neo4j/neo4j.conf && \
    chown -R neo4j:neo4j /var/lib/neo4j/import

# Install GDS plugin
RUN wget -q https://github.com/neo4j/graph-data-science/releases/download/2.3.1/neo4j-graph-data-science-2.3.1.jar \
    -P /var/lib/neo4j/plugins/ && \
    chown neo4j:neo4j /var/lib/neo4j/plugins/neo4j-graph-data-science-2.3.1.jar

# Create import directory and set permissions
RUN mkdir -p /var/lib/neo4j/import && \
    chmod -R 777 /var/lib/neo4j/import

# Clone repo and copy files
#Token is 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
ARG Token
RUN git clone https://${Token}@github.com/SP-2025-CSE511-Data-Processing-at-Scale/project-1-kravipa1.git /app/repo && \
    cp /app/repo/data_loader.py /app/repo/interface.py /app/repo/yellow_tripdata_2022-03.parquet /var/lib/neo4j/import/ && \
    chown -R neo4j:neo4j /var/lib/neo4j/import

WORKDIR /var/lib/neo4j/import

EXPOSE 7474 7687

# Startup command with proper initialization sequence
ENV NEO4J_AUTH=neo4j/project1phase1
CMD service neo4j stop && \
    neo4j-admin set-initial-password project1phase1 && \
    service neo4j start && \
    sleep 10 && \
    while ! curl -s -I http://localhost:7474 | grep -q "200 OK"; do sleep 5; done && \
    python3 data_loader.py && \
    tail -f /dev/null