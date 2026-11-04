import argparse
import asyncio
import sys

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

WRITE_UUID = "0000cf05-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000cf06-0000-1000-8000-00805f9b34fb"

# Frame verificati nel codice del progetto originale
SET_PREFIX = bytes.fromhex("AA BB CC 80 08 00 04 01 02 05")
FOOTER = bytes.fromhex("DD EE FF")

# GET_RUN_INFO: richiede stato ANC + GameMode
GET_STATE = bytes.fromhex(
    "AA BB CC C0 09 00 05 09 00 00 0A 00 DD EE FF"
)


def set_game_frame(enabled):
    return SET_PREFIX + bytes([int(enabled)]) + FOOTER


def parse_game_state(data):
    data = bytes(data)

    if (
            len(data) < 11
            or not data.startswith(bytes.fromhex("AA BB CC"))
            or not data.endswith(FOOTER)
            or data[4] != 0x09
    ):
        return None

    # Nel run-info, 0x0B identifica GameMode
    marker = bytes.fromhex("02 0B")
    pos = data.find(marker, 8, len(data) - 3)

    if pos >= 0 and pos + 2 < len(data) - 3:
        value = data[pos + 2]
        if value in (0, 1):
            return bool(value)

    return None


async def get_game_state(client):
    event = asyncio.Event()
    state = None

    def notification_handler(sender, data):
        nonlocal state
        result = parse_game_state(data)
        if result is not None:
            state = result
            event.set()

    await client.start_notify(NOTIFY_UUID, notification_handler)

    try:
        await client.write_gatt_char(
            WRITE_UUID, GET_STATE, response=False
        )
        await asyncio.wait_for(event.wait(), timeout=4)
        return state
    finally:
        await client.stop_notify(NOTIFY_UUID)


async def find_device(address=None):
    if address:
        # Connessione diretta: evita lo scan implicito di Bleak
        return BLEDevice(address, "HAYLOU S30", None)

    print("Ricerca cuffie Haylou...")
    devices = await BleakScanner.discover(timeout=6)

    matches = [
        d for d in devices
        if "HAYLOU" in (d.name or "").upper()
           or "S30" in (d.name or "").upper()
           or d.address.upper().startswith("BB:AD:EE")
    ]

    if not matches:
        raise RuntimeError(
            "Cuffie non trovate. Prova a specificare --address."
        )

    if len(matches) > 1:
        for d in matches:
            print(f"{d.name}: {d.address}")
        raise RuntimeError(
            "Trovati più dispositivi: specifica --address."
        )

    print(f"Trovato: {matches[0].name} ({matches[0].address})")
    return matches[0]


async def main(args):
    if args.command == "scan":
        devices = await BleakScanner.discover(timeout=8)
        for device in devices:
            print(f"{device.address}  {device.name or 'Sconosciuto'}")
        return

    device = await find_device(args.address)

    async with BleakClient(
            device,
            timeout=12,
            winrt={"use_cached_services": True}
    ) as client:

        if client.services.get_characteristic(WRITE_UUID) is None:
            raise RuntimeError(
                "Caratteristica BLE di controllo non disponibile."
            )

        if args.command in ("status", "toggle"):
            current = await get_game_state(client)
            print(f"GameMode attuale: {'ON' if current else 'OFF'}")

            if args.command == "status":
                return

            enabled = not current

        else:
            enabled = args.command == "on"

        await client.write_gatt_char(
            WRITE_UUID,
            set_game_frame(enabled),
            response=False
        )

        print(
            f"Comando GameMode {'ON' if enabled else 'OFF'} inviato"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Haylou S30 Pro GameMode CLI"
    )
    parser.add_argument(
        "command",
        choices=["on", "off", "toggle", "status", "scan"]
    )
    parser.add_argument(
        "--address",
        help="Indirizzo BLE delle cuffie (consigliato)"
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except Exception as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        sys.exit(1)
