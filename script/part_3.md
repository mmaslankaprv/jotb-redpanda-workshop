# Flink & Zeppelin

## Download Apache Flink

```bash
wget https://www.apache.org/dyn/closer.lua/flink/flink-1.16.1/flink-1.16.1-bin-scala_2.12.tgz
tar -xvf flink-1.16.1-bin-scala_2.12.tgz
```

## Flink

1. Prepare Flink

```bash
export FLINK_HOME="$(realpath ./flink-1.16.1)"


wget https://repo1.maven.org/maven2/org/apache/flink/flink-table-api-scala_2.12/1.16.1/flink-table-api-scala_2.12-1.16.1.jar -O ${FLINK_HOME}/lib/flink-table-api-scala_2.12-1.16.1.jar
wget https://repo1.maven.org/maven2/org/apache/flink/flink-table-api-scala-bridge_2.12/1.16.1/flink-table-api-scala-bridge_2.12-1.16.1.jar -O ${FLINK_HOME}/lib/flink-table-api-scala-bridge_2.12-1.16.1.jar
wget https://repo1.maven.org/maven2/org/apache/flink/flink-table-planner_2.12/1.16.1/flink-table-planner_2.12-1.16.1.jar -O ${FLINK_HOME}/lib/flink-table-planner_2.12-1.16.1.jar
wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.16.1/flink-sql-connector-kafka-1.16.1.jar -O ${FLINK_HOME}/lib/flink-sql-connector-kafka-1.16.1.jar
mv ${FLINK_HOME}/opt/flink-table-planner_2.12-1.16.1.jar  ${FLINK_HOME}/lib
cp ${FLINK_HOME}/opt/flink-python-1.16.1.jar  ${FLINK_HOME}/lib
cp ${FLINK_HOME}/opt/flink-sql-client-1.16.1.jar  ${FLINK_HOME}/lib
mv ${FLINK_HOME}/lib/flink-table-planner-loader-1.16.1.jar ${FLINK_HOME}/opt

```

Configure number of task slots in `${FLINK_HOME}/flink-conf.yaml`

## Start Flink

```bash
    ./flink-1.16.1/bin/start-cluster.sh
```

## Explore data with SQL client

```
wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.16.1/flink-sql-connector-kafka-1.16.1.jar

./flink-1.16.1/bin/sql-client.sh --jar flink-sql-connector-kafka-1.16.1.jar
```


## Example tabels and queries

```sql

DROP TABLE IF EXISTS mta_ace;

CREATE TABLE mta_ace (
  entity_id STRING,
  trip ROW<trip_id STRING, route_id STRING, route_long_name STRING, start_time TIMESTAMP, schedule_relation STRING>,
  vehicle ROW<id STRING, label STRING, license_plate STRING>,
  `position` ROW<lon DOUBLE, lat DOUBLE, bearing DOUBLE, speed DOUBLE, odometer DOUBLE>,
  stop_id STRING,
  stop_name STRING,
  current_status STRING,
  pos_timestamp TIMESTAMP(3),
  congestion_level STRING,
  occupancy_status STRING,
  feed_timestamp TIMESTAMP(3),
  WATERMARK FOR feed_timestamp AS feed_timestamp - INTERVAL '10' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'gtfs_mta_subway',
  'properties.bootstrap.servers' = 'localhost:19092,localhost:19093,localhost:19094',
  'properties.group.id' = 'fling-mta-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'json.ignore-parse-errors' = 'true'
);

SELECT * FROM mta_ace;

DROP VIEW IF EXISTS mta_ace_flat;

CREATE VIEW mta_ace_flat AS
   SELECT
    entity_id,
    trip.trip_id,
    trip.route_id,
    trip.route_long_name,
    trip.start_time,
    trip.schedule_relation,
    vehicle.id,
    vehicle.label,
    vehicle.license_plate,
    `position`.lon,
    `position`.lat,
    `position`.bearing,
    `position`.speed,
    `position`.odometer,
    stop_id,
    stop_name,
    current_status,
    pos_timestamp ,
    congestion_level,
    occupancy_status,
    feed_timestamp,
   FROM `mta_ace`;

SELECT * FROM mta_ace_flat;


CREATE TABLE mta_ace_trip (
    entity_id STRING,
    trip_id STRING,
    route_id STRING,
    route_long_name STRING,
    start_time TIMESTAMP(3),
    schedule_relation STRING,
    PRIMARY KEY (entity_id) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'property-version' = 'universal',
  'properties.bootstrap.servers' = 'localhost:19092,localhost:19093,localhost:19094',
  'topic' = 'mta_ace_trip',
  'value.format' = 'json',
  'key.format' = 'json'
);

INSERT INTO mta_ace_trip
    SELECT entity_id, trip_id, route_id, route_long_name, start_time, schedule_relation
    FROM mta_ace_flat
    WHERE route_id = 'C';
```

## Zeppelin

## Install Zepplelin

Download Zeppelin:
```bash
  wget https://jotb-redpanda-workshop.s3.eu-west-3.amazonaws.com/zeppelin-0.11.0-SNAPSHOT.tar.gz
```

Create Zeppelin virtual_env

```bash
    python -m venv zeppelin_venv
    source zeppelin_venv/bin/activate
    pip install jupyter-client protobuf==3.20.1 ipython ipykernel pyflink apache-flink ipyleaflet
    export GRPC_PYTHON_LDFLAGS=" -framework CoreFoundation"
    pip install grpcio --no-binary :all:
```

Configure pyflink

file `conf/interpreter.json`

```json
"zeppelin.pyflink.python": {
          "name": "zeppelin.pyflink.python",
          "value": "/Users/mmaslanka/dev/jotb_workshop/zeppelin_venv/bin/python",
          "type": "string",
          "description": "Python executable for pyflink"
        }
```

Setup local helium repository

```bash
mkdir zeppelin-0.11.0-SNAPSHOT/helium
```

## Start Zeppelin

```bash
    zeppelin-0.11.0-SNAPSHOT/bin/zeppelin-daemon.sh --config $(realpath zeppelin-0.11.0-SNAPSHOT/conf) restart
```

## Setup Zeppelin

Go to "Interpreters" menu and search for "flink"
setup:

`FLINK_HOME`
`flink.execution.mode`
`flink.execution.remote.host`
`flink.execution.remote.port`

Setup `zeppelin.python` path


