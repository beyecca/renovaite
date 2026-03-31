from .base import Settings, get_settings  # noqa: F401


class DevSettings(Settings):
    debug: bool = True
    secret_key: str = "dev-insecure-change-me"
    mail_console: bool = True
