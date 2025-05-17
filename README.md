# Real-Time Graph-Based NYC Taxi Trip Analytics

This project implements a scalable, real-time data ingestion and graph analytics pipeline using **Neo4j**, **Apache Kafka**, **Docker**, and **Kubernetes**. It models taxi trips within the Bronx region of New York City as a graph and performs **PageRank** and **Breadth-First Search (BFS)** algorithms using Neo4j's Graph Data Science (GDS) library.

---

## Overview

The project was completed in two phases:

### Phase 1: Docker-Based Graph Analytics
- Built a Docker container that sets up a **Neo4j** database and loads filtered NYC Yellow Taxi trip data.
- Processed over **50,000** taxi trips (March 2022) where pickup and dropoff occurred within the **Bronx**.
- Created a graph schema with `Location` nodes and `TRIP` relationships (with distance, fare, pickup, dropoff metadata).
- Implemented:
  - **PageRank** to identify high-traffic areas.
  - **BFS** to find shortest traversal paths between locations.
- Automated all environment setup and data ingestion using a custom `Dockerfile` and `data_loader.py`.

### Phase 2: Real-Time Streaming with Kubernetes and Kafka
- Migrated the system to a **Kubernetes**-orchestrated pipeline using **Minikube**.
- Deployed **Kafka**, **Zookeeper**, **Kafka Connect**, and **Neo4j** using Helm and Kubernetes YAML manifests.
- Developed a Kafka producer (`data_producer.py`) that streams real-time trip records to Kafka topics.
- Configured **Kafka Connect + Neo4j Sink Connector** to ingest the streamed data directly into Neo4j.
- Enabled real-time graph evolution and analytics without downtime.
- Performed BFS and PageRank on dynamic data using the same `interface.py`.

---

