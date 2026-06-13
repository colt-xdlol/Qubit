from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    routerai_api_key: str
    routerai_base_url: str = "https://api.routerai.io/v1"
    routerai_model: str = "deepseek/deepseek-v4-flash"
    admin_ids: str = ""
    daily_free_limit: int = 10
    timezone: str = "Europe/Moscow"
    support_username: str = "megasoki"

    # Главное меню: картинка (положите 1.png в эту относительную папку от корня проекта)
    menu_image_path: str = "assets/1.png"

    # ЮMoney: номер счёта кошелька (получатель, из настроек кошелька)
    yoomoney_wallet: str = ""
    # Секрет HTTP-уведомлений (из настроек «HTTP-уведомления», не публиковать!)
    yoomoney_notification_secret: str = ""
    # Если секрет нужно воспринимать как HEX-строку (редко — по умолчанию как текст UTF-8)
    yoomoney_secret_is_hex: bool = False

    price_per_request_stars: int = 10
    payment_qty_max: int = 500

    # Публичная база URL для подсказок в чате (без закрывающего /), нужен HTTPS‑эндпоинт ниже
    public_base_url: str = ""

    yoomoney_webhook_host: str = "0.0.0.0"
    yoomoney_webhook_port: int = 8080
    yoomoney_webhook_path: str = "/yoomoney/notify"

    @property
    def admin_set(self) -> set[int]:
        raw = self.admin_ids.replace(" ", "").strip()
        if not raw:
            return set()
        return {int(x) for x in raw.split(",") if x.isdigit()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
