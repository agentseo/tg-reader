"""Interactive login. Prompts go to the terminal; the session string goes to stdout
as one JSONL record for `larec ingest`, so it is never shown on screen.

    larec run login | larec ingest            (QR code)
    larec run login --phone | larec ingest    (code from Telegram)

Without larec, `--raw` prints only the session string, to be redirected into a file:
    (umask 077; python -m tg_reader.login --raw > ~/.config/tg-reader/session)
"""

import asyncio
import getpass
import json
import sys

import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from . import config

SESSION_REF = "tg-reader/session"


def ask(prompt: str, secret: bool = False) -> str:
    with open("/dev/tty") as tty:
        if secret:
            return getpass.getpass(prompt, stream=sys.stderr)
        print(prompt, end="", file=sys.stderr, flush=True)
        return tty.readline().strip()


async def phone_login(client: TelegramClient) -> None:
    phone = ask("Phone (+7...): ")
    sent = await client.send_code_request(phone)
    print(f"Code sent via: {type(sent.type).__name__}", file=sys.stderr)
    code = ask("Code from Telegram: ", secret=True)
    await client.sign_in(phone=phone, code=code)


async def qr_login(client: TelegramClient) -> None:
    """Scan with the phone: Settings → Devices → Link Desktop Device."""
    qr = await client.qr_login()
    while True:
        matrix = qrcode.QRCode(border=1)
        matrix.add_data(qr.url)
        matrix.print_ascii(out=sys.stderr, invert=True)
        print(
            "Scan: Telegram on phone → Settings → Devices → Link Desktop Device",
            file=sys.stderr,
        )
        try:
            await qr.wait(timeout=60)
            return
        except asyncio.TimeoutError:
            print("QR expired, new one:", file=sys.stderr)
            await qr.recreate()


async def run(use_phone: bool, raw: bool) -> None:
    api_id, api_hash = config.api_credentials()
    client = TelegramClient(StringSession(), api_id, api_hash, receive_updates=False)
    await client.connect()
    try:
        if use_phone:
            await phone_login(client)
        else:
            await qr_login(client)
    except SessionPasswordNeededError:
        await client.sign_in(password=ask("2FA password: ", secret=True))
    me = await client.get_me()
    print(f"Logged in as {me.first_name} (id {me.id}).", file=sys.stderr)
    session = client.session.save()
    print(session if raw else json.dumps({"ref": SESSION_REF, "value": session}))
    await client.disconnect()


def main() -> None:
    if sys.stdout.isatty():
        config.die(
            "stdout is a terminal — pipe it into larec (`larec run login | larec ingest`) "
            "or redirect `--raw` output into a file (see README.md)"
        )
    args = sys.argv[1:]
    asyncio.run(run(use_phone="--phone" in args, raw="--raw" in args))


if __name__ == "__main__":
    main()
