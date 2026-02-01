variable "project_name" { type = string }
variable "github_owner" { type = string }
variable "github_repo"  { type = string }
variable "aws_region"   { type = string }

data "aws_caller_identity" "current" {}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Only allow this repo to assume the role
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_owner}/${var.github_repo}:*"]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = "${var.project_name}-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# Minimal permissions for:
# - push image to ECR
# - update App Runner
# - upload web to S3 + invalidate CloudFront (we'll attach more later)
resource "aws_iam_role_policy" "deploy" {
  name = "${var.project_name}-deploy-policy"
  role = aws_iam_role.deploy.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # ECR push
      {
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:CompleteLayerUpload",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ],
        Resource = "*"
      },
      # App Runner updates (resource scoping is possible later; keep simple now)
      {
        Effect = "Allow",
        Action = [
          "apprunner:*",
          "iam:PassRole"
        ],
        Resource = "*"
      },
      # S3 + CloudFront 
      {
        Effect = "Allow",
        Action = [
          "s3:*",
          "cloudfront:CreateInvalidation"
        ],
        Resource = "*"
      }
    ]
  })
}

output "role_arn" {
  value = aws_iam_role.deploy.arn
}
