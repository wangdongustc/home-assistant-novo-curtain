# Novo RS-485 Motor Curtain Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant integration for controlling Novo N99 RS-485 motor curtains.

## Features

- Control curtain position (open/close/set position)
- Button-based open/close/jog/stop control for direct motor actions
- Real-time position and motor state feedback via a sensor
- RS-485 serial communication
- Support for multiple curtains on the same bus

## Installation

### Option 1: HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS:
   - URL: `https://github.com/wangdongustc/home-assistant-novo-curtain`
   - Category: Integration
3. Search for "Novo Curtain" in HACS and install it.
4. Restart Home Assistant.

### Option 2: Manual Installation

1. Download the `novo_curtain` directory from the `custom_components` folder in this repository.
2. Copy it to your Home Assistant's `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for "Novo Curtain" and select it.
3. Configure the following settings:
   - **Serial Path**: The path to your RS-485 serial device (e.g., `/dev/ttyUSB0`)
   - **Address**: The device address (hexadecimal, e.g., `0x01`)
   - **Channel**: The channel number (0-255)

## Usage

After configuration, the curtain will appear as a cover entity in Home Assistant. You can:

- Open/close the curtain
- Set specific positions (0-100%)
- Monitor current position
- Use action buttons for direct open, close, inching left/right, and stop control
- Monitor real-time motor state via a dedicated sensor

## Hardware Requirements

- Novo N99 curtain motor with RS-485 interface
- RS-485 to USB adapter or similar serial interface
- Proper RS-485 wiring and termination

## Troubleshooting

### Connection Issues

- Verify the serial path is correct
- Check RS-485 wiring and termination
- Ensure the device address and channel match your hardware configuration

### Logs

Check Home Assistant logs for detailed error messages. The integration logs under the `novo_curtain` logger.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Development Tips

To create virtual devices for testing:
```
socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pipe
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you have issues or questions:

1. Check the [Issues](https://github.com/wangdongustc/home-assistant-novo-curtain/issues) page
2. Create a new issue with detailed information about your setup and the problem
