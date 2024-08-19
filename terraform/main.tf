provider "aws" {
  region = var.aws_region
}

# S3 Bucket
resource "aws_s3_bucket" "payroll_raw_data_bucket" {
  bucket = var.s3_bucket_name
}

# Versioning configuration for the S3 Bucket
resource "aws_s3_bucket_versioning" "payroll_raw_data_bucket_versioning" {
  bucket = aws_s3_bucket.payroll_raw_data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.payroll_raw_data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
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
  description = "Policy for Redshift serverless to access S3 bucket"

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
          aws_s3_bucket.payroll_raw_data_bucket.arn,
          "${aws_s3_bucket.payroll_raw_data_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_redshift_s3_access" {
  role       = aws_iam_role.redshift_s3_access_role.name
  policy_arn = aws_iam_policy.redshift_s3_access_policy.arn
}


# Subnet definitions
resource "aws_subnet" "subnet_1" {
  vpc_id            = var.vpc_id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-west-2a"  # Corrected availability zone
  map_public_ip_on_launch = true
}

resource "aws_subnet" "subnet_2" {
  vpc_id            = var.vpc_id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-west-2b"  # Corrected availability zone
  map_public_ip_on_launch = true
}

resource "aws_subnet" "subnet_3" {
  vpc_id            = var.vpc_id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "eu-west-2c"  # Corrected availability zone
  map_public_ip_on_launch = true
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

# Redshift Serverless Namespace
resource "aws_redshiftserverless_namespace" "example" {
  namespace_name      = var.redshift_namespace_name
  admin_username      = var.redshift_master_username
  admin_user_password = var.redshift_master_password
}

# Redshift Serverless Workgroup
resource "aws_redshiftserverless_workgroup" "example" {
  workgroup_name     = var.redshift_workgroup_name
  namespace_name     = aws_redshiftserverless_namespace.example.namespace_name
  base_capacity      = 32
  security_group_ids = [aws_security_group.redshift_sg.id]
  subnet_ids          = [
    aws_subnet.subnet_1.id,
    aws_subnet.subnet_2.id,
    aws_subnet.subnet_3.id
  ]

  tags = {
    payroll = "payroll-workgroup"
  }
}
