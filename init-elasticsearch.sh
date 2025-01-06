#!/bin/bash

# Attendre qu'Elasticsearch soit prêt
until curl -XGET -u elastic:${ELASTIC_PASSWORD} "http://elasticsearch:9200" >/dev/null 2>&1; do
    echo "Attente de la disponibilité d'Elasticsearch..."
    sleep 5
done

# Mettre à jour le mot de passe de kibana_system
curl -XPOST -u elastic:${ELASTIC_PASSWORD} "http://elasticsearch:9200/_security/user/kibana_system/_password" \
  -H "Content-Type: application/json" \
  -d '{"password": "'"${KIBANA_SYSTEM_PASSWORD}"'"}'

echo "Mot de passe mis à jour pour kibana_system."
