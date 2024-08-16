provider "aws" {
  region = var.aws_region
}

# S3 Bucket
resource "aws_s3_bucket" "payroll_raw_data_bucket" {
  bucket = var.s3_bucket_name

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# IAM Role for Redshift S3 Access
resource "aws_iam_role" "redshift_s3_access_role" {
  name = var.iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "redshift.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "redshift_s3_access_policy" {
  name        = "RedshiftS3AccessPolicy"
  description = "Policy for Redshift cluster to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.raw_data_bucket.arn,
          "${aws_s3_bucket.raw_data_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_redshift_s3_access" {
  role       = aws_iam_role.redshift_s3_access_role.name
  policy_arn = aws_iam_policy.redshift_s3_access_policy.arn
}

# Security Group for Redshift
resource "aws_security_group" "redshift_sg" {
  name   = "redshift_sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Adjust to restrict access to your IP range
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Redshift Cluster
resource "aws_redshift_cluster" "redshift_cluster" {
  cluster_identifier      = var.redshift_cluster_id
  node_type               = var.redshift_node_type
  number_of_nodes         = var.redshift_number_of_nodes
  master_username         = var.redshift_master_username
  master_password         = var.redshift_master_password
  database_name           = var.redshift_database_name
  iam_roles               = [aws_iam_role.redshift_s3_access_role.arn]
  skip_final_snapshot     = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.redshift_sg.id]
}

# Table Creation (local-exec)
resource "null_resource" "create_redshift_tables" {
  provisioner "local-exec" {
    command = <<EOT
      psql \
        --host=${aws_redshift_cluster.redshift_cluster.endpoint} \
        --port=5439 \
        --username=${var.redshift_master_username} \
        --dbname=${var.redshift_database_name} \
        -f ${path.module}/../sql/create_datawarehouse.sql
    EOT

    environment = {
      PGPASSWORD = var.redshift_master_password
    }
  }

  depends_on = [aws_redshift_cluster.redshift_cluster]
}
