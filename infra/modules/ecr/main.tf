variable "name" { type = string }

resource "aws_ecr_repository" "this" {
  name                 = var.name
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

output "repository_url" {
  value = aws_ecr_repository.this.repository_url
}
