"""Print all dialogs (id, type, title) so the owner can pick ids for profiles.toml.

Meant for the owner's own terminal: it lists every chat of the account.
"""

import argparse
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from . import config


async def run(query: str | None) -> None:
    api_id, api_hash = config.api_credentials()
    client = TelegramClient(
        StringSession(config.session_string()), api_id, api_hash, receive_updates=False
    )
    await client.connect()
    async for dialog in client.iter_dialogs():
        if query and query.lower() not in dialog.name.lower():
            continue
        kind = (
            "channel"
            if dialog.is_channel and not dialog.is_group
            else "group"
            if dialog.is_group
            else "user"
        )
        print(f"{dialog.id}\t{kind}\t{dialog.name}")
    await client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="List Telegram dialogs with their ids")
    parser.add_argument("query", nargs="?", help="substring filter on the title")
    asyncio.run(run(parser.parse_args().query))


if __name__ == "__main__":
    main()
