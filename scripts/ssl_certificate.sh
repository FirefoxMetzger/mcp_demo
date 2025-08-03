#!/bin/bash

# Parse command line arguments
STAGING_FLAG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --staging)
            STAGING_FLAG="--staging"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cat <<EOF > scripts/cloudflare.ini
dns_cloudflare_api_token=${TF_VAR_cloudflare_api_token}
EOF
chmod 600 scripts/cloudflare.ini

mkdir -p scripts/certs/logs
mkdir -p scripts/certs/work
mkdir -p scripts/certs/config


DOMAIN=${domain}
uv run certbot certonly \
    --agree-tos \
    $STAGING_FLAG \
    --non-interactive \
    --dns-cloudflare \
    --dns-cloudflare-credentials scripts/cloudflare.ini \
    -d $DOMAIN \
    --work-dir scripts/certs/work \
    --logs-dir scripts/certs/logs \
    --config-dir scripts/certs/config

mv scripts/certs/config/archive/$DOMAIN/privkey1.pem \
   src/static/ssl_privatekey.pem
mv scripts/certs/config/archive/$DOMAIN/fullchain1.pem \
   src/static/ssl_fullchain.pem

rm -f scripts/cloudflare.ini
rm -rf scripts/certs/