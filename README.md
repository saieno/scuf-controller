# Scuf Controller - DualShock Support for Linux

scuf-controller is a package that configures generic and official Dualshock controllers as Xbox Controllers for use within Linux. This works for Official DualShock 4 and DualShock 5 controllers, SCUF brand controllers, and other generic DualShock controllers. 

## Installation

On Debian/Ubuntu based distros, download the .deb package and install as you normally would. If using the command line, you can run the following:

```bash
sudo dpkg -i scuf-controller_1.0_all.deb
```

## Usage
#### Note: Make sure Steam is not open when starting the service.

```bash
# start service
sudo systemctl start scuf-controller

# check service status
sudo systemctl status scuf-controller

# restart service
sudo systemctl restart scuf-controller

# stop service
sudo systemctl stop scuf-controller
```
Once the service is started, you'll want to wait a minute for the cron to clean up the controller inputs. If you have the service enabled to run at system start-up, then the clean up should be completed by the time you get into a game.
#### Note: When using with Steam, be sure to disable Steam Input for Xbox Controllers.
*You can do so by right clicking the game, going to Properties, Controller, and make sure Xbox Controller is disabled or blank.*

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

If you have any issues or would like to add support for additional controllers, please open an issue for discussion and tracking.

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
