variable "app" {
    type = object({
      namespace = string
      app_name = string
      domain = string
      secret_key = string
      storage = object({
        static_root = string
        sqlite_path = string
      })
    })
}

variable "tls" {
    type = object({
      email = string
      private_key_secret_ref = string
    })
}