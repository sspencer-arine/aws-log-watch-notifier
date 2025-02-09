# aws-log-watch-notifier

AWS Log Watch Notifier

## Run

Installation is currently on `54.80.171.144` in our prod AWS account (ec2) as the `sspencer` user.

It is running via `systemd --user` as the following unit file:

`~/.config/systemd/user/aws-log-watch-notifier-wrapper@.service`

```
[Unit]
Description=AWS Log Watch Notifier Wrapper (%i)
After=network.target

[Service]
WorkingDirectory=/home/sspencer/aws-log-watch-notifier
ExecStart=/home/sspencer/aws-log-watch-notifier/%i.sh

Restart=always
RestartSec=60

[Install]
WantedBy=default.target
```

Need to enable linger mode for user as root:

```
root@ip-172-31-35-68:~# loginctl enable-linger sspencer
```

Added the scripts via:

```
systemctl --user daemon-reload
systemctl --user enable --now aws-log-watch-notifier-wrapper@run-generic-log-dev
systemctl --user enable --now aws-log-watch-notifier-wrapper@run-generic-log-prod
systemctl --user enable --now aws-log-watch-notifier-wrapper@run-update-cmr-attributes-dev
systemctl --user enable --now aws-log-watch-notifier-wrapper@run-update-cmr-attributes-prod
```

Reloading can be done after updating source code in `~/aws-log-watch-notifier`

```
systemctl --user restart 'aws-log-watch-notifier-wrapper@*'
```
