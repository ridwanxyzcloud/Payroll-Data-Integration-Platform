variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-west-2"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "iam_role_name" {
  description = "Name of the IAM Role for Redshift"
  type        = string
}

variable "redshift_cluster_id" {
  description = "Redshift cluster identifier"
  type        = string
}

variable "redshift_node_type" {
  description = "Redshift node type"
  type        = string
}

variable "redshift_number_of_nodes" {
  description = "Number of nodes in the Redshift cluster"
  type        = number
}

variable "redshift_master_username" {
  description = "Redshift master username"
  type        = string
}

variable "redshift_master_password" {
  description = "Redshift master password"
  type        = string
  sensitive   = true
}

variable "redshift_database_name" {
  description = "Name of the Redshift database"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where Redshift is deployed"
  type        = string
}
