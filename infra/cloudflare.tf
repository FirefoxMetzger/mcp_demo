# Cloudflare Provider Configuration
variable "cloudflare_api_token" {}
variable "cloudflare_subdomain" {}

locals {
  mcp_domain = "${var.cloudflare_subdomain}.${data.cloudflare_zone.domain.name}"
}

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
  name    = local.mcp_domain
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


