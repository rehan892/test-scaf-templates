output "app_name" {
  description = "App Name"
  value       = "{{ project_dash }}"
}

output "application" {
  value = "{{ project_dash }}"
}

output "aws_region" {
  description = "AWS Region"
  value       = "{{ aws_region }}"
}

output "aws_profile" {
  description = "AWS Profile for CLI"
  value       = "{{ project_dash }}"
}

output "account_id" {
  value = "{{ aws_account_id }}"
}

output "domain_name" {
  value = "{{ domain_name }}"
}
