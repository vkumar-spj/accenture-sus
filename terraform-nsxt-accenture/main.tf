terraform {
  required_providers {
    nsxt = {
      source = "vmware/nsxt"
      version = "3.1.1"
    }
  }
}

locals {
  nat_csv = csvdecode(file("${path.module}/${var.input_file}"))
  nat_rules = { for nat_rule in local.nat_csv: nat_rule.description => nat_rule  }
}

provider "nsxt" {
  host           = var.nsx_mgr
  username       =  var.nsx_user
  password       =  var.nsx_password
  allow_unverified_ssl = var.ssl_value
}


data "nsxt_edge_cluster" "edge_cluster1" {
  display_name = "edge-cluster-01"
}

data "nsxt_policy_edge_cluster" "edge_cluster1" {
  display_name = "edge-cluster-01"
}

resource "nsxt_policy_nat_rule" "dnat1" {
  for_each             = local.nat_rules
  description          = each.key
  display_name         = each.value.display_name
  action               = each.value.action
  source_networks      = ["${each.value.source_networks}"]
#  destination_networks = ["${each.value.destination_networks}"]
  translated_networks  = ["${each.value.translated_networks}"]
  gateway_path         = each.value.gateway_path
  logging              = each.value.logging
#  scope                = ["${each.value.scope}"]

  tag {
    scope = "color"
    tag   = "blue"
  }
}


resource "nsxt_logical_tier0_router" "tier0_router" {
  display_name           = "VJ_RTR_tier0"
  description            = "ACTIVE-STANDBY Tier0 router provisioned by Terraform"
  high_availability_mode = "ACTIVE_STANDBY"
  edge_cluster_id        = data.nsxt_edge_cluster.edge_cluster1.id

  tag {
    scope = "color"
    tag   = "blue"
  }
}




resource "nsxt_logical_tier1_router" "tier1_router" {
  description                 = "RTR1 provisioned by Terraform"
  display_name                = "VJ_RTR_tier1"
  failover_mode               = "PREEMPTIVE"
  edge_cluster_id             = data.nsxt_edge_cluster.edge_cluster1.id
  enable_router_advertisement = true
  advertise_connected_routes  = false
  advertise_static_routes     = true
  advertise_nat_routes        = true
  advertise_lb_vip_routes     = true
  advertise_lb_snat_ip_routes = false

  tag {
    scope = "color"
    tag   = "blue"
  }
}





resource "nsxt_policy_tier0_gateway" "tier0_gw" {
  description              = "Tier-0  gatewayprovisioned by Terraform"
  display_name             = "Tier0-gw1-terraform"
  failover_mode            = "PREEMPTIVE"
  default_rule_logging     = false
  enable_firewall          = true
  force_whitelisting       = false
  ha_mode                  = "ACTIVE_STANDBY"
  internal_transit_subnets = ["102.64.0.0/16"]
  transit_subnets          = ["101.64.0.0/16"]
  edge_cluster_path        = data.nsxt_policy_edge_cluster.edge_cluster1.path
  rd_admin_address         = "192.168.0.2"


  tag {
    scope = "color"
    tag   = "blue"
  }
}
