# Remote state with locking. Create the S3 bucket + DynamoDB table once
# (manually or via a bootstrap module) before running `terraform init`.
#
# terraform {
#   backend "s3" {
#     bucket         = "my-tfstate-bucket-vaishalisaini-tech"
#     key            = "gitops-platform/terraform.tfstate"
#     region         = "ap-northeast-2"          # Seoul
#     dynamodb_table = "terraform-locks"
#     encrypt        = true
#   }
# }
