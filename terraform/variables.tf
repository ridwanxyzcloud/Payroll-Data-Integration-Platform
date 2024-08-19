variable "aws_region" {
  description = "The AWS region to deploy the resources in."
  type        = string
  default     = "us-west-2"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket."
  type        = string
}

variable "iam_role_name" {
  description = "Name of the IAM Role for Redshift."
  type        = string
}

variable "redshift_namespace_name" {
  description = "Name of the Redshift Serverless namespace."
  type        = string
}

variable "redshift_workgroup_name" {
  description = "Name of the Redshift Serverless workgroup."
  type        = string
}

variable "redshift_master_username" {
  description = "Master username for Redshift Serverless."
  type        = string
}

variable "redshift_master_password" {
  description = "Master password for Redshift Serverless."
  type        = string
  sensitive   = true
}

variable "vpc_id" {
  description = "The ID of the VPC."
  type        = string
}
