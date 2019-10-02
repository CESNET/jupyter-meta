resource "openstack_compute_instance_v2" "k8s_cluster_worker" {
  count      = "${var.k8s_worker_node_count}"
  name       = "${var.k8s_cluster_name}-worker-${count.index + 1}"
  image_name = "${var.image_name}"
  flavor_name     = "${var.flavor_2cpu4ram}"
  key_pair        = "${var.key_pair}"
  security_groups = ["ingress_ssh", "allow_barn", "default", "allow_ingress_http_https"]

  metadata = {
    group        = "g_${var.k8s_cluster_name}_worker"
    ansible_user = "ubuntu"
  }

  network {
    name = "${var.network_name}"
  }
}

resource "openstack_networking_floatingip_v2" "k8s_cluster_worker_fip" {
  count = "${var.k8s_worker_node_count}"
  pool  = "${var.pool}"
}

resource "openstack_compute_floatingip_associate_v2" "k8s_cluster_worker_fip_a" {
  count       = "${var.k8s_worker_node_count}"
  floating_ip = "${element(openstack_networking_floatingip_v2.k8s_cluster_worker_fip.*.address, count.index)}"
  instance_id = "${element(openstack_compute_instance_v2.k8s_cluster_worker.*.id, count.index)}"
}

# Get PTR records
data "dns_ptr_record_set" "ptr_k8s_cluster_worker" {
  count = "${var.k8s_worker_node_count}"
  ip_address = "${element(openstack_networking_floatingip_v2.k8s_cluster_worker_fip.*.address, count.index)}"
}

# Set CNAME records
resource "dns_cname_record" "cname_k8s_cluster_worker" {
  count = "${var.k8s_worker_node_count}"
  zone  = "${var.zone}"
  name  = "${element(openstack_compute_instance_v2.k8s_cluster_worker.*.name, count.index)}"
  cname = "${element(data.dns_ptr_record_set.ptr_k8s_cluster_worker.*.ptr, count.index)}"
  ttl   = "${var.ttl}"
}
