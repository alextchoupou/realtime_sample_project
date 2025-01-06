#!/usr/bin/env bash

host=$1
port=$2
timeout=$3

for i in $(seq 1 "$timeout"); do
  echo "Waiting for $host:$port... ($i/$timeout)"
  nc -z "$host" "$port" && echo "$host:$port is available!" && exit 0
  sleep 1
done

echo "$host:$port did not become available within $timeout seconds."
exit 1
