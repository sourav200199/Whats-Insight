import re
import pandas as pd

def preprocess(data, recipient_name=None):
    # WhatsApp new format: [20/07/25, 12:59:34 PM] User: message
    pat_date = r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APM]{2}\]'
    
    dates = re.findall(pat_date, data)
    messages = re.split(pat_date, data)[1:]  # split leaves first empty, so skip it
    
    pdf = pd.DataFrame({'Date': dates, 'Text': messages})
    
    # Clean date strings and convert
    pdf['Date'] = pdf['Date'].str.strip("[]")
    pdf['Msg_date'] = pd.to_datetime(pdf['Date'], format='%d/%m/%y, %I:%M:%S %p')
    pdf.drop(columns=['Date'], inplace=True)

    users = []
    msgs = []

    for message in pdf['Text']:
        # Split into [username, message] if possible
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        
        if len(entry) >= 3:
            sender = entry[1].strip()

            # Remove system & group name messages
            if sender == recipient_name:
                users.append("group_notification")
                msgs.append(entry[2])
            else:
                users.append(sender)
                msgs.append(entry[2])
        else:
            # Pure system notification
            users.append("group_notification")
            msgs.append(entry[0])

    pdf['User'] = users
    pdf['Message'] = msgs

    # Drop unwanted system/group name rows
    pdf = pdf[(pdf['User'] != 'group_notification') & (pdf['User'] != recipient_name)]
    # Drop unwanted rows: group notifications, group name, and "You" system actions
    system_keywords = ["created", "added", "removed", "changed", "joined", "left", "pinned", "deleted"]
    pdf = pdf[
        (pdf['User'] != 'group_notification') &
        (pdf['User'] != recipient_name) &
        ~(pdf['Message'].str.lower().str.contains('|'.join(system_keywords)))
    ]

    # Add time-based features
    pdf['Year'] = pdf['Msg_date'].dt.year
    pdf['Month'] = pdf['Msg_date'].dt.month_name()
    pdf['Day'] = pdf['Msg_date'].dt.day
    pdf['Hour'] = pdf['Msg_date'].dt.hour
    pdf['Minute'] = pdf['Msg_date'].dt.minute
    pdf.drop(columns=['Msg_date'], inplace=True)

    return pdf
