output "s3_bucket_name" {
  description = "The name of the S3 bucket."
  value       = aws_s3_bucket.payroll_raw_data_bucket.bucket
}


output "redshift_namespace_name" {
  value = aws_redshiftserverless_namespace.example.namespace_name
}

output "redshift_workgroup_name" {
  value = aws_redshiftserverless_workgroup.example.workgroup_name
}

output "redshift_endpoint" {
  value = aws_redshiftserverless_workgroup.example.endpoint
}

