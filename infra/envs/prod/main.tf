module "ecr" {
  source = "../../modules/ecr"
  name   = "${var.project_name}-api"
}

module "github_oidc" {
  source       = "../../modules/github_oidc"
  project_name = var.project_name
  github_owner = var.github_owner
  github_repo  = var.github_repo
  aws_region   = var.aws_region
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "github_deploy_role_arn" {
  value = module.github_oidc.role_arn
}
