# Cloudflare Provider Configuration
variable "cloudflare_api_token" {}
variable "cloudflare_subdomain" {}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Get zone information
data "cloudflare_zone" "domain" {
  zone_id = "3d05d8273e295311ee236cece79bc97c"
}

# Example A record
resource "cloudflare_dns_record" "mcp-demo" {
  zone_id = data.cloudflare_zone.domain.zone_id
  name    = var.cloudflare_subdomain
  content = google_compute_address.public.address
  type    = "A"
  ttl     = 1 # Auto
  proxied = false
}

# Wait for DNS propagation before setting PTR record
resource "time_sleep" "dns_propagation" {
  depends_on = [cloudflare_dns_record.mcp-demo]
  
  create_duration = "10s"
}

locals {
  mcp_domain = "${cloudflare_dns_record.mcp-demo.name}.${data.cloudflare_zone.domain.name}"
}
