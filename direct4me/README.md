# Direct4Me Integration for Home Assistant

The network of self-service Direct4.me parcel lockers enables our consignees to quickly and discreetly pick up their parcels 24/7.

[Direct4Me Webiste](https://www.direct4.me)

![image](https://play-lh.googleusercontent.com/-Vw1FxjDPcHzPKvUjpw5t6KwcjlE_wtEU9j-MOIdZSf5pXPUGtfv2x7fFcQqp4ZJGso)

# Installation

### Manually

> [Download](https://github.com/milosljubenovic/direct4me-ha/archive/main.zip) and copy `custom_components/direct4me` folder to custom_components folder in your HomeAssistant config folder

### Automagically

```shell
# Auto install via terminal shell
wget -q -O - https://cdn.jsdelivr.net/gh/al-one/hass-xiaomi-miot/install.sh | DOMAIN=catlink REPO_PATH=milosljubenovic/direct4me-ha ARCHIVE_TAG=main bash -
```

# Configuration:

configuration.yaml

```yaml
direct4me:
  username: "00xxxxxxxxxx" # Phone number in format 00<countrycode><your_phonenumber>
  password: "xxxxxxx"
  update_interval: 01:00:00 # Optional: Default 1h (hh:mm:ss)
```

<p align="center">
  <strong>Disclaimer</strong>
</p>
<p align="justify">
  This project is intended solely for personal use and to simplify the usage of the <a href="https://www.direct4.me">Direct4me</a> API for users who rely on Home Assistant. There is no intention to harm the business, violate the API's terms of service, or infringe upon any rights. All efforts have been made to ensure that this integration is in compliance with fair-use principles. The logo, trademark, and any other proprietary content belonging to Direct4me are copyrighted and are the property of their respective owners.
</p>
<p align="justify">
  By using this project, you agree to respect the rights of the trademark and copyright holders, and you understand that this project is an independent creation not affiliated with or endorsed by Direct4me.
</p>
