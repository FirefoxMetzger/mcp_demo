docker build -t gcr.io/${TF_VAR_google_project_id}/mcp-server:latest .
docker push gcr.io/${TF_VAR_google_project_id}/mcp-server:latest
