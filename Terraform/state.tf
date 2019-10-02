terraform {
  backend "swift" {
    container         = "k8s-prod-test_terraform_state"
    archive_container = "k8s-prod-test_terraform-state-archive"
  }
}
