# Installing Redpanda

## Macos

```bash
brew install redpanda-data/tap/redpanda
```

## Linux

### Ubunut/Debian

```bash
curl -1sLf \
    'https://dl.redpanda.com/nzc4ZYQK3WRGd9sy/redpanda/cfg/setup/bash.deb.sh' \
    | sudo -E bash

sudo apt-get install redpanda
```

### Fedora/RHEL

```bash
curl -1sLf \
'https://dl.redpanda.com/nzc4ZYQK3WRGd9sy/redpanda/cfg/setup/bash.rpm.sh' \
| sudo -E bash

sudo yum install redpanda
```

## Redpanda cluster

```bash
cd redpanda-cluster
docker-compose up -d
```

## Addresses

```bash

export REDPANDA_API_ADMIN_ADDRS=$(docker inspect jotb-redpanda-cluster-redpanda-1-1 jotb-redpanda-cluster-redpanda-2-1 jotb-redpanda-cluster-redpanda-0-1 | jq --raw-output '.[].NetworkSettings.Ports."9644/tcp"[].HostPort' | awk '{print "localhost:"$1}' | tr '\n' ',' | sed 's/,$//')
export REDPANDA_BROKERS="localhost:19092,localhost:19093,localhost:19094"

```

### RPK

```bash
rpk cluster info
rpk cluster health

rpk topic list
rpk topic create jotb-test -p 6 -r 3
watch 'echo $(date) | rpk topic produce jotb-test'

# simple consumer

rpk topic consume jotb-test

# consumer groups

rpk topic consume jotb-test -g group-1
rpk topic consume jotb-test -g group-1

# describing group

```

### Console

Navigate to `localhost:8888`
