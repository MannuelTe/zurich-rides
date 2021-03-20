#! /usr/bin/python3

# Authentication: https://gspread.readthedocs.io/en/latest/oauth2.html#enable-api-access
# Get worksheet: https://gspread.readthedocs.io/en/latest/user-guide.html#opening-a-spreadsheet

import os
import datetime
import pytz
import gspread
import pandas as pd

from smtplib import SMTP_SSL as SMTP 
from email.mime.text import MIMEText

import config

timezone_zurich = pytz.timezone('Europe/Zurich')

mail_text_begin = "Hi\n\nFor the ride on {date:s} from {location:s} you ride with:\n"
mail_text_end = "\nWe look forward to riding with you.\n\nBest,\nHead wind\n\nP.S.: If you have any syntoms after the ride, please respond to this message."

mail_text_one_rider = "Hi\n\nNow you have to be strong. For the ride on {date:s} from {location:s} you unfortunately ride alone. I'm sorry!\n\nBest,\nTooth fairy <3"

class ServiceMailClient:
    def __init__(self):
        self.conn = SMTP(config.smtp_server)
        self.conn.set_debuglevel(False)
        self.conn.login(
            config.sender_username,
            config.sender_password
            )

    def __del__(self):
        self.conn.quit()

    def send_message(self, to, subject: str, content: str, cc=[], bcc=[], 
                     text_subtype='plain'):
        
        if isinstance(to, str):
            to = [to]

        if isinstance(cc, str):
            cc = [cc]
        
        if isinstance(bcc, str):
            bcc = [bcc]

        if content:
            msg = MIMEText(content, text_subtype,)
        else:
            msg = MIMEText('No content', text_subtype,)

        if subject:
            msg['Subject'] = subject
        else:
            msg['Subject'] = 'No subject'
            
        msg['From'] = config.sender_displayname
        msg['To'] = ','.join(to)
        if cc:
            msg['CC'] = ','.join(cc)
        if bcc:
            msg['BCC'] = ','.join(bcc)
        
        self.conn.sendmail(
            config.sender_username, 
            to + cc + bcc,
            msg.as_string()
        )


def print_log(msg: str) -> None:
    now = datetime.datetime.now()
    out = '[{ts:s}]\t{msg:s}'
    print(out.format(ts=now.strftime('%Y-%m-%d %H:%M:%S'),msg=msg.replace('\n',' ')))


def get_df(sh: gspread.models.Spreadsheet, worksheet_index: int, header=True):
    _ws = sh.get_worksheet(worksheet_index)
    _data = _ws.get_all_values()
    if header:
        _df = pd.DataFrame(_data[1:])
        _df.columns = _data[0]
    else:
        _df = pd.DataFrame(_data)
    return _df


def get_prev_dt() -> float:
    if os.path.exists(config.PREV_DT_PATH):
        with open(config.PREV_DT_PATH, 'r') as f: 
            _out = float(f.read())
    else:
        # Five minutes ago as default
        _out = datetime.datetime.now().timestamp() - (5 * 60)
    return(_out)


def save_dt(dt_timestamp: float()) -> None:
    with open(config.PREV_DT_PATH, 'w') as f: 
        f.write(str(dt_timestamp))


if __name__ == '__main__':
    dt_now = datetime.datetime.now().timestamp()
    dt_prev = get_prev_dt()
    
    # Connect to the relevant Google spreadsheat
    gc = gspread.service_account(filename=config.CREDENTIAL_PATH)
    sh = gc.open_by_key(config.ID_SPREADSHEET)

    # Load and format data of routes
    df_routes = pd.concat(
        [get_df(sh, 1), get_df(sh, 2)[['Column text (automatic)', 'Time stamps']]],
        axis=1,
        join='inner',
    ) 
    df_routes['Timestamp'] = df_routes['Timestamp'].apply(
        lambda x: timezone_zurich.localize(
            datetime.datetime.strptime(x, '%m/%d/%Y %H:%M:%S')
        )
    )
    df_routes['Time stamps'] = df_routes['Time stamps'].apply(
        lambda x: timezone_zurich.localize(
            datetime.datetime.strptime(x, '%m/%d/%Y %H:%M:%S')
        )
    )
    
    # Does the ride start in the next ~30 minutes?
    r_filter = [dt_prev < x.timestamp() - config.TIME_BEFORE_RIDE <= dt_now for x in df_routes['Time stamps']]
    df_routes = df_routes[r_filter] 

    if not df_routes.empty:
        # Load and format dataframe of participants
        df_participants = get_df(sh, 0)
        df_participants['Timestamp'] = df_participants['Timestamp'].apply(
            lambda x: timezone_zurich.localize(
                datetime.datetime.strptime(x, '%m/%d/%Y %H:%M:%S')
            )
        )

        for _, ride in df_routes.iterrows():
            # Does anybody participate?
            p_filter = [ride['Column text (automatic)'] in x for x in df_participants['Ride']]

            if any(p_filter):
                # Finalize the message
                date_text = ride['Column text (automatic)'].split(': ')[0]
                ride_participants = df_participants[p_filter]
                if len(ride_participants) > 1:      
                    mail_text_middle = ''
                    for rider_name in ride_participants['Full name']: 
                        mail_text_middle += '* ' + rider_name + '\n'
                    full_text = mail_text_begin.format(date=date_text, location=ride['Meeting point']) + mail_text_middle + mail_text_end
                else:
                    full_text = mail_text_one_rider.format(date=date_text, location=ride['Meeting point']) 
                
                # Send messages to participant(s)
                client = ServiceMailClient()
                for em_address in list(ride_participants['Email Address']):
                    client.send_message(
                        [em_address],
                        ride['Column text (automatic)'],
                        full_text,
                    )
                del client

                # Write action to log file
                print_log(
                    str(len(ride_participants)) + ' mails sent for ' + ride['Column text (automatic)']
                )

    # Save the time stamp where the script started
    save_dt(dt_now)
