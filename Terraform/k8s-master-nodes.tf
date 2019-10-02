resource "openstack_compute_instance_v2" "k8s_cluster_master" {
  count      = "${var.k8s_master_node_count}"
  name       = "${var.k8s_cluster_name}-master-${count.index + 1}"
  image_name = "${var.image_name}"
  flavor_name     = "${var.flavor_2cpu4ram}"
  key_pair        = "${var.key_pair}"
  security_groups = ["ingress_ssh", "allow_barn", "default", "allow_ingress_http_https"]

  metadata = {
    group        = "g_${var.k8s_cluster_name}_master"
    ansible_user = "ubuntu"
  }

  network {
    name = "${var.network_name}"
  }
}

resource "openstack_networking_floatingip_v2" "k8s_cluster_master_fip" {
  count = "${var.k8s_master_node_count}"
  pool  = "${var.pool}"
}

resource "openstack_compute_floatingip_associate_v2" "k8s_cluster_master_fip_a" {
  count       = "${var.k8s_master_node_count}"
  floating_ip = "${element(openstack_networking_floatingip_v2.k8s_cluster_master_fip.*.address, count.index)}"
  instance_id = "${element(openstack_compute_instance_v2.k8s_cluster_master.*.id, count.index)}"
}

data "dns_ptr_record_set" "ptr_k8s_cluster_master" {
  count = "${var.k8s_master_node_count}"
  ip_address = "${element(openstack_networking_floatingip_v2.k8s_cluster_master_fip.*.address, count.index)}"
}

resource "dns_cname_record" "cname_k8s_cluster_master" {
  count = "${var.k8s_master_node_count}"
  zone  = "${var.zone}"
  name  = "${element(openstack_compute_instance_v2.k8s_cluster_master.*.name, count.index)}"
  cname = "${element(data.dns_ptr_record_set.ptr_k8s_cluster_master.*.ptr, count.index)}"
  ttl   = "${var.ttl}"
}
