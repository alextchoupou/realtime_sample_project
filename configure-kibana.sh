#!/bin/bash

# Attendre qu'Elasticsearch soit opérationnel
echo "Attente du démarrage d'Elasticsearch..."
until curl -XGET -u "elastic:${ELASTICSEARCH_PASSWORD}" -s "http://elasticsearch:9200" >/dev/null; do
  sleep 5
done
echo "Elasticsearch est prêt."

# Mettre à jour le mot de passe de l'utilisateur kibana_system
echo "Mise à jour du mot de passe de l'utilisateur kibana_system..."
curl -XPOST -u "elastic:${ELASTICSEARCH_PASSWORD}" -s "http://elasticsearch:9200/_security/user/kibana_system/_password" -H "Content-Type: application/json" -d '{
  "password": "'"${KIBANA_PASSWORD}"'"
}' && echo "Mot de passe mis à jour avec succès."

# Générer des clés de chiffrement
ENCRYPTION_KEY=$(openssl rand -hex 32)
REPORTING_KEY=$(openssl rand -hex 32)
SECURITY_KEY=$(openssl rand -hex 32)

# Chemin du fichier de configuration
CONFIG_FILE="/usr/share/kibana/config/kibana.yml"

# Ajouter une ligne vide si le fichier n'est pas vide
if [ -s "$CONFIG_FILE" ]; then
  echo "" >> "$CONFIG_FILE"
fi

# Ajouter les configurations si elles n'existent pas déjà
add_config() {
  local key="$1"
  local value="$2"
  if ! grep -q "^${key}:" "$CONFIG_FILE"; then
    echo "${key}: ${value}" >> "$CONFIG_FILE"
  else
    echo "La configuration '${key}' existe déjà, elle ne sera pas redéfinie."
  fi
}

add_config "elasticsearch.username" "\"kibana_system\""
add_config "elasticsearch.password" "\"${KIBANA_PASSWORD}\""
add_config "xpack.encryptedSavedObjects.encryptionKey" "\"${ENCRYPTION_KEY}\""
add_config "xpack.reporting.encryptionKey" "\"${REPORTING_KEY}\""
add_config "xpack.security.encryptionKey" "\"${SECURITY_KEY}\""

echo "Configuration automatique de Kibana terminée."
exec /bin/tini -- /usr/share/kibana/bin/kibana
