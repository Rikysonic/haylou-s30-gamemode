# Haylou S30 GameMode CLI

A lightweight Python command-line utility to enable, disable, and toggle **GameMode** on Haylou S30 headphones via Bluetooth Low Energy (BLE).

Created by ChatGPT (it must be said).

Based on the wonderful work made by [revolutedigital](https://github.com/revolutedigital/haylou-s30-pro-windows).

Designed for Windows, it provides a simple way to control GameMode without installing the official Haylou application or running a graphical interface.

Ideal for integration with **AutoHotkey**, keyboard shortcuts, and automation scripts.

## Features

- Enable or disable GameMode
- Toggle GameMode based on its current state
- Read the current GameMode status
- Direct BLE connection using the headphones' MAC address
- Fast connections using Windows GATT service caching
- Standalone executable support via PyInstaller

## Requirements

- Windows 10/11
- Python 3.10+ (or a compiled executable)
- Bluetooth adapter with BLE support
- Haylou S30 headphones

## Installation

Install the required Python dependency:

```powershell
pip install bleak==3.0.2
```

Run the utility using Python:

```powershell
python haylou.py on --address "XX:XX:XX:XX:XX:XX"
```

Alternatively, build a standalone Windows executable:

```powershell
pip install pyinstaller
pyinstaller --onefile --name haylou haylou.py
```

The resulting executable will be available at `dist\haylou.exe`.

OR (could result in a faster sw due to no extracting needed):

```powershell
pip install pyinstaller
pyinstaller --name haylou haylou.py
```

The resulting executable + `_internal` folder will be available at `dist`.

## Usage

```powershell
haylou.exe <command> [--address MAC]
```

### Available commands

| Command | Description |
|---|---|
| `on` | Enable GameMode |
| `off` | Disable GameMode |
| `toggle` | Switch GameMode to the opposite of its current state |
| `status` | Read the current GameMode state |
| `scan` | Scan for nearby Bluetooth devices (not recommended, it's difficult to understand which device is the correct one) |

### Options

| Option | Description |
|---|---|
| `--address MAC` | Specify the headphones' Bluetooth MAC address (recommended) |
| `-h`, `--help` | Display command-line help |

### Examples

Enable GameMode:

```powershell
haylou.exe on --address "XX:XX:XX:XX:XX:XX"
```

Disable GameMode:

```powershell
haylou.exe off --address "XX:XX:XX:XX:XX:XX"
```

Toggle GameMode:

```powershell
haylou.exe toggle --address "XX:XX:XX:XX:XX:XX"
```

Check GameMode status:

```powershell
haylou.exe status --address "XX:XX:XX:XX:XX:XX"
```

## Finding your Bluetooth MAC address

Using the MAC address is strongly recommended instead of relying on Bluetooth scanning.

On Windows:

1. Connect your Haylou S30 headphones to your computer.
2. Open **Device Manager** (`devmgmt.msc`).
3. Expand the **Bluetooth** section.
4. Find your Haylou headphones and open **Properties**.
5. Navigate to the **Details** tab.
6. Look for **Bluetooth Device Address** (or its localized equivalent) in the property dropdown.
7. Copy the address and use it with the `--address` option.

Depending on the Bluetooth adapter and Windows driver, the address may be displayed without separators. For example, `AABBCCDDEEFF` becomes `AA:BB:CC:DD:EE:FF`.

Make sure you use the address associated with the headphones' BLE interface.

### Why avoid `scan`?

Bluetooth scanning can be unreliable on Windows, particularly when the headphones are already connected as an audio device.

The `scan` command is included for troubleshooting, but it may fail to discover the headphones even when they are connected and working correctly.

Also, the headphones could be displayed without their name, so if the scan returns a great number of nearby devices, it's basically impossibile to know which MAC address corresponds to the headphones.

**For everyday usage, always prefer `--address`.**

## AutoHotkey integration

Example for **AutoHotkey v2**, binding `Ctrl + Alt + G` to GameMode toggle:

```autohotkey
^!g::{
    Run '"C:\Tools\haylou.exe" toggle --address "XX:XX:XX:XX:XX:XX"', , "Hide"
}
```

Replace the executable path and MAC address with your own values.

## Technical details

The utility communicates directly with the headphones using the proprietary Haylou BLE protocol.

- **BLE library:** Bleak
- **GATT write characteristic:** `0000cf05-0000-1000-8000-00805f9b34fb`
- **GATT notification characteristic:** `0000cf06-0000-1000-8000-00805f9b34fb`
- **GameMode attribute:** `0x05`
- **GameMode values:** `0x01` (ON), `0x00` (OFF)

Windows GATT service caching (`use_cached_services=True`) is enabled to reduce connection latency.

Each CLI invocation connects to the headphones, executes the requested operation, and disconnects.

## Credits

BLE protocol implementation based on the research and work from:

[revolutedigital/haylou-s30-pro-windows](https://github.com/revolutedigital/haylou-s30-pro-windows)

This utility is an independent lightweight implementation focused exclusively on GameMode control.

Not affiliated with or endorsed by Haylou.
