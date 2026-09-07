# scuf-controller — DualShock-style gamepads as Xbox 360 controllers on Linux

`scuf-controller` makes a SCUF, DualShock 4, DualSense or generic DualShock-clone
gamepad show up as a Microsoft Xbox 360 controller, so games and launchers that
only speak XInput see the right buttons and axes — and see them only once.

It takes exclusive control of the physical pad and re-emits corrected events on a
virtual controller (USB `045e:028e`, the same identity the kernel's `xpad` driver
presents). Because the physical device is grabbed, its raw events stop reaching
applications, which is what removes the duplicated input these pads otherwise
produce.

## Requirements

Any Linux with systemd, `python3` and `python-evdev` — packaged as
`python3-evdev` on Debian, Ubuntu and Fedora, `python-evdev` on Arch and
openSUSE, and `py3-evdev` on Alpine. There is nothing to compile.

> **Upgrading from 1.x?** Version 2.0 no longer uses `xboxdrv`. See
> [Migrating from 1.x](#migrating-from-1x) below.

## Installation

Download the `.deb` from the releases page and install it:

```bash
sudo apt install ./scuf-controller_2.0_all.deb
```

Using `apt install ./…` rather than `dpkg -i` lets apt pull in `python3-evdev`
automatically.

### Arch

```bash
cd packaging && makepkg -si
```

### Fedora, RHEL and openSUSE

```bash
rpmbuild -ba packaging/scuf-controller.spec
sudo dnf install ~/rpmbuild/RPMS/noarch/scuf-controller-*.noarch.rpm
```

### Any other distro

```bash
sudo make install
sudo systemctl enable --now scuf-controller
```

`make install` honours `DESTDIR` and the usual path variables (`PREFIX`,
`SYSCONFDIR`, `UNITDIR`, `UDEVDIR`, …), and is what all three packages call, so
there is one set of paths to keep straight. `make uninstall` reverses it,
leaving your `/etc` files alone. `make check` validates the script and profiles.

### Building the Debian package yourself

```bash
sudo apt install devscripts debhelper
dpkg-buildpackage -us -uc -b
sudo apt install ../scuf-controller_2.0_all.deb
```

## Usage

```bash
sudo systemctl start scuf-controller     # start now
sudo systemctl enable scuf-controller    # start at boot
sudo systemctl status scuf-controller    # check on it
sudo systemctl stop scuf-controller      # hand the raw pad back
```

The service picks up the controller as soon as it is plugged in and reattaches
after an unplug, so there is nothing to wait for and nothing to clean up.

To see what it found and how it read the pad:

```bash
scuf-controller --list
journalctl -u scuf-controller -n 20
```

### Using it with Steam

Disable Steam Input for Xbox controllers, or Steam will remap on top of the
mapping this service already provides: right-click the game → *Properties* →
*Controller* → set Xbox Controller support to disabled.

Steam only scans for controllers at startup, so if it was already running when
you first started the service, restart Steam once. You do not need to close
Steam before starting or restarting the service — the grab works regardless.

## Configuration

Everything lives in `/etc/scuf-controller.conf`; restart the service after
editing it.

| Setting | Purpose |
| --- | --- |
| `device` | Pin a specific pad instead of auto-detecting. Prefer a stable `/dev/input/by-id/…` path. |
| `profile` | `auto` (default), or a profile name from `--list-profiles`. |
| `invert_left_y`, `invert_right_y` | Flip a stick's vertical axis if up and down come out backwards. |
| `[buttons]` | Per-button overrides on top of the profile. |
| `[axes]` | Per-axis overrides on top of the profile. |

### Profiles

A profile describes one controller's layout. They are files, not code, so
adding a controller does not need a new release:

| Location | Purpose |
| --- | --- |
| `/usr/share/scuf-controller/profiles/` | Shipped with the package. Don't edit; upgrades replace them. |
| `/etc/scuf-controller.d/` | Yours. A file here shadows a shipped one of the same name. |

Two are shipped. **`generic-dualshock`** covers SCUF and other DualShock clones:
the kernel has no driver for these, so `hid-generic` exposes the HID report
descriptor as-is, putting the right stick on `ABS_Z`/`ABS_RZ`, the analog
triggers on `ABS_RX`/`ABS_RY`, and shifting the face buttons into `BTN_C` and
`BTN_Z`. **`sony-dualshock`** covers official DualShock 4 and DualSense pads on
`hid-sony` or `hid-playstation`, which already report a sane layout.

`scuf-controller --list-profiles` shows what is installed, and
`scuf-controller --list` shows which one each connected pad would get.

With `profile = auto`, the most specific match wins: a profile naming the pad's
USB id beats one matching on device name, which beats one matching on
capabilities alone. So a profile written for your exact controller always takes
precedence over a generic layout that merely happens to fit.

### Adding a controller

Generate a starting point rather than writing one by hand:

```bash
sudo systemctl stop scuf-controller
scuf-controller --dump-profile > /etc/scuf-controller.d/mypad.conf
sudo scuf-controller --debug
```

`--dump-profile` fills in the pad's USB ids and, if an existing profile partly
fits, prefills the mapping from it and marks the rest `TODO`. Correct the file
against what `--debug` prints as you press each control, then:

```bash
sudo systemctl start scuf-controller
```

To try a profile before installing it, point the daemon at a directory:

```bash
sudo scuf-controller --profile-dir ./profiles --debug
```

A profile looks like this:

```ini
[profile]
description = My Controller

[match]
vendor = 2e95
product = 7725

[axes]
ABS_X = ABS_X stick        # sticks scale to -32768..32767
ABS_RX = ABS_Z trigger     # triggers scale to 0..255
ABS_HAT0X = ABS_HAT0X hat  # hats are -1..1

[buttons]
BTN_SOUTH = BTN_X

[digital-triggers]
BTN_TL = ABS_Z             # merged with the analog value; harder press wins
```

`[match]` also accepts `name` (a regex on the device name), `buttons` and
`axes` (codes the pad must report) and `not_buttons` (codes it must not) — use
those when a pad has no stable USB id. Run `make check` to validate profiles
before sending them as a pull request.

### Checking or changing the mapping

```bash
sudo systemctl stop scuf-controller
sudo scuf-controller --debug
```

This logs every translated event as you press things. To move a button, add it
to the `[buttons]` section using the source name `--debug` prints:

```ini
[buttons]
BTN_THUMBL = BTN_MODE
```

DS4-style shells report a touchpad click that the Xbox 360 layout has no room
for, so it is left unmapped by default; the line above is how you give it a home.

## How it hides the physical pad

Grabbing the device silences its events, but it stays visible to udev, so SDL and
Steam would list it next to the virtual pad as a second, permanently-idle
gamepad. `/usr/lib/udev/rules.d/60-scuf-controller.rules` clears
`ID_INPUT_JOYSTICK` on the known controllers so they skip it.

The trade-off is that the raw pad stays hidden from gamepad enumeration even when
the service is stopped. To change or disable that, shadow the file in `/etc`,
which udev reads in preference:

```bash
sudo cp /usr/lib/udev/rules.d/60-scuf-controller.rules /etc/udev/rules.d/
sudoedit /etc/udev/rules.d/60-scuf-controller.rules
sudo udevadm control --reload && sudo udevadm trigger
```

An empty file at that path disables the rules entirely. Adding a controller is a
matter of copying a line and filling in the ids from `lsusb`.

## Migrating from 1.x

Version 1.x drove the pad with [`xboxdrv`](https://github.com/xboxdrv/xboxdrv).
That package was dropped from Debian and Ubuntu during the Python 2 deprecation
and last shipped in Ubuntu 24.04, so on any current release the old package can
no longer satisfy its dependency and will not install.

2.0 replaces it with a small `python3-evdev` daemon. What changed for you:

- **No `xboxdrv`.** The mapping it was configured with is now built in, as the
  `generic` and `sony` profiles.
- **No cron job.** 1.x installed a per-minute root cron entry that deleted
  `/dev/input/js0` to fight duplicate input. Grabbing the device prevents the
  duplication at the source, so the cron entry and `cleanup-ds4.sh` are gone.
- **Config moved.** The generated `/usr/local/ds4.conf` is replaced by
  `/etc/scuf-controller.conf`, which is a dpkg conffile and survives upgrades.
- **The unit is tracked properly.** 1.x used `Type=forking` around a
  backgrounded `nohup`; 2.0 is `Type=simple` with `Restart=always`, so
  `systemctl status` reports the truth.

Removing the 1.x package cleans up its files. If you had hand-edited
`/usr/local/ds4.conf`, port those changes to a profile in
`/etc/scuf-controller.d/`.

## A note on button codes

The virtual pad reports X as `BTN_X` (0x133) and Y as `BTN_Y` (0x134). Those are
aliases for `BTN_NORTH` and `BTN_WEST`, which is positionally backwards from the
modern semantic names — but it is exactly what `xpad` does, and matching it is
what makes controller databases recognise the device as a real Xbox pad. If you
read the mapping tables and think two buttons are swapped, this is why.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

Adding a controller is a profile file, not a code change — see
[Adding a controller](#adding-a-controller). Pull requests adding a tested
profile to `profiles/` are very welcome; please run `make check` first, and add
the pad's USB ids to `60-scuf-controller.rules` in the same PR.

## License

[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
