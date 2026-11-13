"""Credentials from the environment (set by `larec run` or by hand) and chat profiles
from profiles.toml. The session may also come from a file named by TG_SESSION_FILE."""

import os
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES_PATH = ROOT / "profiles.toml"


def die(message: str) -> None:
    print(f"tg-reader: {message}", file=sys.stderr)
    sys.exit(2)


def api_credentials() -> tuple[int, str]:
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    if not api_id or not api_hash:
        die("TG_API_ID / TG_API_HASH are not set — set them in the environment")
    try:
        return int(api_id), api_hash
    except ValueError:
        die("TG_API_ID must be a number")


def session_string() -> str:
    value = os.environ.get("TG_SESSION")
    if not value and os.environ.get("TG_SESSION_FILE"):
        path = Path(os.environ["TG_SESSION_FILE"]).expanduser()
        try:
            value = path.read_text().strip()
        except OSError as exc:
            die(f"cannot read TG_SESSION_FILE: {exc.strerror}")
    if not value:
        die("neither TG_SESSION nor TG_SESSION_FILE is set — log in first (see README.md)")
    return value


def load_profile(name: str) -> tuple[list[int | str], bool]:
    """Chat entries of one profile (numeric peer ids, '@username' or an exact title)
    and whether the profile may send messages (`write = true`, default false)."""
    if not PROFILES_PATH.exists():
        die(f"{PROFILES_PATH} not found")
    with PROFILES_PATH.open("rb") as fh:
        profiles = tomllib.load(fh).get("profiles", {})
    if name not in profiles:
        die(
            f"profile '{name}' is not in profiles.toml (known: {', '.join(profiles) or 'none'})"
        )
    chats = profiles[name].get("chats", [])
    if not chats:
        die(f"profile '{name}' has an empty chat list")
    return chats, profiles[name].get("write", False) is True
