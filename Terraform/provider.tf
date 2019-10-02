provider "openstack" {
  auth_url = "https://identity.cloud.muni.cz/v3"
  region = "brno1"
}

# Configure the DNS Provider
provider "dns" {
  update {
    server        = "147.251.4.41"
    transport     = "tcp"
    key_name      = "edirex-test.ics.muni.cz."
    key_algorithm = "hmac-md5"
    key_secret    = "${var.dns_key_secret}"
  }
}
