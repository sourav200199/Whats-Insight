import re
import pandas as pd

def preprocess(data):
    # pattern to match the date and time in the format 'dd/mm/yyyy, hh:mm - '
    pat_date = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    dates = re.findall(pat_date, data)
    msg = re.split(pat_date, data)[1:]
    pdf = pd.DataFrame({'Date':dates, 'Text':msg})

    pdf['Date'] = pd.to_datetime(pdf['Date'], format='%d/%m/%Y, %H:%M - ')
    pdf.rename(columns={'Date':'Msg_date'}, inplace=True)

    users = []
    messages = []

    for message in pdf['Text']:
        pat2 = re.split('([\w\W]+?):\s', message)
    
        if pat2[1:]: #the username
            users.append(pat2[1])
            messages.append(pat2[2])
        else:
            users.append('group_notification')
            messages.append(pat2[0])
        
    pdf['User'] = users
    pdf['Message'] = messages
    pdf.drop(columns=['Text'], inplace=True)

    pdf['Year'] = pdf['Msg_date'].dt.year
    pdf['Month'] = pdf['Msg_date'].dt.month_name()
    pdf['Day'] = pdf['Msg_date'].dt.day
    pdf['Hour'] = pdf['Msg_date'].dt.hour
    pdf['Min'] = pdf['Msg_date'].dt.minute
    pdf.drop(columns=['Msg_date'], inplace=True)

    return pdf
