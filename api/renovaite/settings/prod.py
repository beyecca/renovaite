from .base import Settings, get_settings  # noqa: F401


class ProdSettings(Settings):
    debug: bool = False
    # secret_key must be provided via SECRET_KEY env var — no default
    secret_key: str
