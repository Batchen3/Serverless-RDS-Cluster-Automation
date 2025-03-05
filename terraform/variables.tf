variable "db_instance_identifier" {
  description = "The name of the RDS instance"
  type        = string
}

variable "db_engine" {
  description = "The database engine to use"
  type        = string
}

variable "db_instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
}