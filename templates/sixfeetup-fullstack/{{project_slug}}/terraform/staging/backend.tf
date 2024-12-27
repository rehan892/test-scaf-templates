terraform {
  required_version = ">= 1.4"
  backend "s3" {
    region         = "{{ aws_region }}"
    bucket         = "{{ project_dash }}-terraform-state"
    key            = "{{ project_dash }}.staging.json"
    encrypt        = true
    dynamodb_table = "{{ project_dash }}-terraform-state"
  }
}
