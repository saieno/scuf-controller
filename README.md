# scuf-vantage2
SystemD Script to Enable Native Support for SCUF Vantage 2 Controller

To use:

Install the package, which will also install the xboxdrv dependency.


systemctl start scuf-controller

systemctl status scuf-controller

systemctl stop scuf-controller


If your controller becomes unplugged, you may have to restart the service once its plugged in again.
