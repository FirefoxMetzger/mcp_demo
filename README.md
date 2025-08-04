# MCP Demo

**Deploy your own MCP server in minutes.**

⭐ _Please leave a star if you like this repo_ ⭐.

This project is for developers, tinkerers, and hobbyists who want a fast,
reliable, and secure MCP (Model Context Protocol) server for their internal
tools, AI Service integrations (e.g., Elevenlabs), or tech demos. It has
all the IaC (infrastructure-as-code), scripts, and sensible defaults needed to
go from zero to production with minimal effort.

The deployment targets apps that need to serve low-to-medium traffic (100 - 1000
req/s) with decent avaiability (99.95% uptime). This means you should expect this
server to handle up to 500 concurrent users without issues.

## Why this project?

- **Skip DevOps Overkill:** No need for a 6-instance, multi-AZ k8s cluster to
  serve 100 users. Start small, then scale.
- **Bring your own MCP:** HTTPS and API key auth for integration with tools like
  ElevenLabs, n8n, and more.
- **Fast Prototyping:** Don't just demo the project, let them try on *their*
  machine.
- **Statefullness**: Don't loose MCP's transaction state to lambda functions
  shutdown.
- **Learning by Doing:** Don't let deployment stop you from learning about AI.

## Cost

Running this server 24/7 will cost about 1-2 beers per month for infrastructure.
My code for free, but GCP will still charge you for the server.

That said, the project has an intentionally small footprint that fits entirely
into the GCP free-tier if you are eligible. The main thing you need to pay for
is a custom domain so that you can `https://mcp-server...`.

## Features

- ⚡ FastMCP server with demo tool ([weather_mcp.py](src/services/weather_mcp.py))
- 🔑 API-key validation (OAuth-compliant JWT)
- 🚦 Rate limiting
- 🧪 Dummy OAuth server ([authorization_server.py](src/services/authorization_server.py))
- 🛠️ Script to generate signed API keys (90-day validity)
- 🔒 Script for SSL certificates from Let’s Encrypt (90-day validity)
- ☁️ Terraform IaC for GCP ([google.tf](infra/google.tf)) and Cloudflare ([cloudflare.tf](infra/cloudflare.tf))
- 🛡️ IP whitelisting

## 🚀 Get Started

> **Note**: Please check out the accompanying blog post for a quick-start guide.

Check out my [blog post](#) for the quick-start guide and walkthrough of
the repo with tips on customizing your own setup. Whether you want to build your
own tools, deploy a prototype, or just lean and experiment, you’ll find
everything you need to get going.


Ready to deploy? Clone the repo and follow along!
