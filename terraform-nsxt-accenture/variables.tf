variable "nsx_mgr" {
        type = string
        description = "NSX Manager name"
}

variable "nsx_user" {
        type = string
        description = "NSX User name"
}

variable "nsx_password" {
        type = string
        description = "NSX Manager password"
}

variable "ssl_value" {
        type = string
        description = "SSL verification required"
}

variable "input_file" {
        type = string
        description = "Input file with firewall rules(CSV format ):"
}

