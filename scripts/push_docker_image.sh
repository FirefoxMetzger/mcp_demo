docker build \
    --platform linux/amd64,linux/arm64 \
    --build-arg domain=${domain} \
    -t gcr.io/${TF_VAR_google_project_id}/mcp-server:latest .
docker push gcr.io/${TF_VAR_google_project_id}/mcp-server:latest
