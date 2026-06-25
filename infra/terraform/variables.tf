variable "region" {
  description = "AWS region (ap-northeast-2 = Seoul)"
  type        = string
  default     = "ap-northeast-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "gitops-platform"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.30"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "tags" {
  type = map(string)
  default = {
    Project   = "gitops-platform"
    ManagedBy = "terraform"
  }
}
