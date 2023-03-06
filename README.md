# Klipper Power Off on Completion
This script will take the printer status from Klipper/Moonraker and power off the printer on print completion.

----

## Directions for use

1. Install prerequsits
   1. ```sudo apt update && sudo apt install -y git```
   2. ```sudo pip3 install requests```
2. Clone code to Raspberry Pi running Klipper and Moonraker
   1. ```cd /home/pi```
   2. ```git clone https://github.com/11chrisadams11/klipper-power-off-on-completion.git```
   3. ```cd klipper-power-off-on-completion```
3. Make script executable
   1. ```chmod 744 ./klipper_power.py```
4. Modify settings in script to your liking
6. If you want to run it manually, start script before starting print (otherwise use the service below)
   1. ```./klipper_power.py```

## Directions to run as a systemd service

1. Copy contents of klipper_poweroff.service to /etc/systemd/system/klipper_poweroff.service
2. Modify User, Group, WorkingDirectory, and ExecStart to match your setup
3. Run ```systemctl daemon-reload``` to enable the service
4. Run ```systemctl enable klipper_poweroff``` to have the service start on boot
5. Run ```systemctl start klipper_poweroff``` to start the service

## Directions to change settings (when using service)

1. Modify settings in script
2. Run ```systemctl restart klipper_poweroff``` to restart the service
