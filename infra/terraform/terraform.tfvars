app = {
  namespace = "qmra"
  app_name = "qmra"
  domain = "dev2.qmra"
  secret_key = "1234asldkjasdo87"
  storage = {
    static_root = "/var/cache/qmra/static"
    sqlite_path = "/var/lib/qmra.db"
  }
}

tls = {
  email = "antoine.daurat@kompetenz-wasser.de"
  private_key_secret_ref = "letsencrypt-private-key-secret"
}