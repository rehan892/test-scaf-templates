terraform {
  required_version = ">= 1.4"
  backend "s3" {
    region         = "{{ aws_region }}"
    bucket         = "{{ project_dash }}-terraform-state"
    key            = "{{ project_slug }}.sandbox.json"
    encrypt        = true
    dynamodb_table = "{{ project_dash }}-terraform-state"
  }
}

module "global_variables" {
  source = "../modules/global_variables"
}
