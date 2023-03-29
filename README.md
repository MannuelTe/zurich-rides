# ZüRides 🚴

The script runs every five minute by a cronjob (*/5 * * * *).

## Example for `config.py` file

```{python}
#! /usr/bin/python3

import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

smtp_server = 'smtp.gmail.com'
sender_displayname = 'Name shown to recepient'
sender_username = 'your.mail@gmail.com'
sender_password = 'yourpassword'

# Spreadsheet credentials
CREDENTIAL_PATH = PROJECT_DIR + '/service_account.json'

# Spreadsheet
ID_SPREADSHEET = 'Googlespreadsheet ID from URL'
```
 ## check out the text generator on zuridesgenerator.streamlit.app

 in the future i want to find a way to scrape the stats from the page but right now i dont know how :(())