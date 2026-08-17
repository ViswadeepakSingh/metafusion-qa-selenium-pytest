import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (the folder that contains config/)
load_dotenv(Path(__file__).parent.parent / ".env", override=False)


class Config:
    """
    Loads settings from config/<ENV>.json and credentials from .env (or environment variables).

    Credentials are read from .env at the project root — set them once there
    and they apply to every run automatically.  The .env file is in .gitignore
    so credentials are never committed to source control.

    To switch environments, change ENV in .env (or set it as a shell variable):
        ENV=local     → config/local.json
        ENV=staging   → config/staging.json
    """

    def __init__(self):
        env = os.getenv("ENV", "staging")
        config_path = Path(__file__).parent / f"{env}.json"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}. "
                f"Available envs: {[f.stem for f in Path(__file__).parent.glob('*.json')]}"
            )

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        # ── URLs & browser settings (from JSON) ──────────────────────────
        self.BASE_URL: str = data.get("base_url", "")
        self.BROWSER: str = data.get("browser", "chromium")
        self.HEADLESS: bool = data.get("headless", False)
        self.SLOW_MO: int = data.get("slow_mo", 0)
        self.TIMEOUT: int = data.get("timeout", 30000)

        # ── Credentials (from environment variables) ──────────────────────
        self.USERNAME: str = os.getenv("APP_USERNAME", "")
        self.PASSWORD: str = os.getenv("APP_PASSWORD", "")

        if not self.USERNAME or not self.PASSWORD:
            raise EnvironmentError(
                "APP_USERNAME and APP_PASSWORD are not set.\n"
                "  Add them to the .env file in the project root:\n"
                "    APP_USERNAME=your_username\n"
                "    APP_PASSWORD=your_password\n"
                "  The .env file is in .gitignore — credentials will never be committed."
            )