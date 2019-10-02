variable "network_name" {
  default = "auto_allocated_network"
}

variable "pool" {
  default = "public-cesnet-78-128-251"
}

variable "key_pair" {
  default = "tf-edirex"
}

variable "dns_key_secret" {
}

variable "zone" {
  default = "edirex.ics.muni.cz."
}

variable "ttl" {
  default = 300
}

variable "image_name" {
  default = "ubuntu-bionic-x86_64"
}

variable "image_uuid" {
  default = "e8d75fc1-ac32-4851-90b5-b4c925e9e6f8"
}

variable "k8s_cluster_name" {
  default = "k8s-prod-test"
}

variable "k8s_master_node_count" {
  default = "2"
}

variable "k8s_worker_node_count" {
  default = "3"
}

variable "flavor_4cpu16ram" {
  default = "standard.xlarge"
}

variable "flavor_4cpu8ram" {
  default = "standard.large"
}

variable "flavor_2cpu4ram" {
  default = "standard.medium"
}

variable "flavor_1cpu1ram" {
  default = "standard.tiny"
}
