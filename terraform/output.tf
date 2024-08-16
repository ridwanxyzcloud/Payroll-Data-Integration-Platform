output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.raw_data_bucket.bucket
}

output "redshift_cluster_endpoint" {
  description = "Endpoint of the Redshift cluster"
  value       = aws_redshift_cluster.redshift_cluster.endpoint
}

output "iam_role_arn" {
  description = "ARN of the IAM Role"
  value       = aws_iam_role.redshift_s3_access_role.arn
}
