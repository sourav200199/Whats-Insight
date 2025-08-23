from urlextract import URLExtract
import pandas as pd
from pandas.api.types import CategoricalDtype
from wordcloud import WordCloud
from collections import Counter
import emoji

stp = open('stop_hinglish.txt','r')
stop_words = stp.read()

# Function to fetch chat statistics
def fetch_stats(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]

    n = data.shape[0] 

    words = []
    for msgs in data['Message']:
        words.extend(msgs.split())

    m = data[data['Message'] == '<Media omitted>\n'].shape[0]
    
    url = []
    extractor = URLExtract()
    for msgs in data['Message']:
        url.extend(extractor.find_urls(msgs))
    url = pd.DataFrame(url)
    url.rename(columns={0:'URL'}, inplace=True)

    return n, words, m, url

# Function to fetch busiest users
def busy_users(data):
    val1 = data['User'].value_counts()
    pu = round((data['User'].value_counts()/data.shape[0])*100,2).reset_index()

    return val1, pu

# Function to create wordcloud
def create_cloud(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]

    data = data[data['User'] != 'group_notification']
    data = data[data['Message'] != '<Media omitted>\n']

    

    wc = WordCloud(width=500, height=400)
    df_wc = wc.generate(data['Message'].str.cat(sep=" "))

    return df_wc

# Function to find most commonly used words
def find_common_words(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]
    # Remove strings which are like omitted, may not be the exact word

    newdf = data[~data['Message'].str.contains('audio omitted')] # 2.Remove 'Media omitted'
    newdf = newdf[~newdf['Message'].str.contains('image omitted')] # 3.Remove 'Image omitted'
    newdf = newdf[~newdf['Message'].str.contains('video omitted')] # 4.Remove 'Video omitted'
    newdf = newdf[~newdf['Message'].str.contains('sticker omitted')] # 5.Remove 'Sticker omitted'

    # 3.Remove the stop words
    words = []
    for msgs in newdf['Message']:
        for wrd in msgs.lower().split():
            if wrd not in stop_words:
                words.append(wrd)

    # Remove emojis from messages
    words = [word for word in words if word not in emoji.UNICODE_EMOJI['en']]

    # Remove words with less than 2 characters
    words = [word for word in words if len(word) > 1]

    words_used = pd.DataFrame(Counter(words).most_common(25))
    words_used.rename(columns={0:'Word', 1:'Count'}, inplace=True)
    words_used.sort_values('Count', ascending=False, inplace=True)

    return words_used

# Function to find emoji analysis
def emoji_analysis(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]

    emojis = []
    for msgs in data['Message']:
        emojis.extend([c for c in msgs if c in emoji.UNICODE_EMOJI['en']])

    emj = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emj.rename(columns={0:'Emoji', 1:'Count'}, inplace=True)
    
    return emj

# Function to find the message count based on each month
def monthly_analysis(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]    

    month_df = data.groupby(['Month', 'Year']).count()['Message'].reset_index()

    time = []
    for i in range(month_df.shape[0]):
        time.append(month_df['Month'][i] + '/' + str(month_df['Year'][i]))   
    
    month_df['mm/yyyy'] = time
    key = lambda x: pd.to_datetime(x['mm/yyyy'])
    month_df['mm/yyyy'] = month_df.apply(key, axis=1)
    month_df = month_df.sort_values(by = 'mm/yyyy')
    
    return month_df

# Function to find the message count based on each date
def daily_analysis(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]    

    # Join the day, month and year col. to get the date in dd/mm/yyyy format
    data['Date'] = data['Day'].astype(str) + '-' + data['Month'].astype(str) + '-' + data['Year'].astype(str)
    day_df = data.groupby(['Date']).count()['Message'].reset_index()

    # Convert the date to datetime format and sort it
    key = lambda x: pd.to_datetime(x['Date'])
    day_df['Date'] = day_df.apply(key, axis=1)
    # Remove the timestamp from the date
    day_df['Date'] = day_df['Date'].dt.date
    day_df = day_df.sort_values(by = 'Date')
    
    return day_df

# Function to find the busiest days
def busy_days_months(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]

    # Join the day, month and year col. to get the date in dd/mm/yyyy format
    data['Date'] = data['Day'].astype(str) + '-' + data['Month'].astype(str) + '-' + data['Year'].astype(str)
    data['Date'] = pd.to_datetime(data['Date'])
    # Busiest days
    day_df = data['Date'].dt.day_name().value_counts().reset_index()
    day_df.rename(columns={'index':'Day', 'Date':'Message Count'}, inplace=True)     
    day_df = day_df.sort_values(by = ['Message Count'], ascending=False)

    # Busiest months
    month_df = data['Date'].dt.month_name().value_counts().reset_index()
    month_df.rename(columns={'index':'Month', 'Date':'Message Count'}, inplace=True)
    month_df = month_df.sort_values(by = ['Message Count'], ascending=False)

    return day_df, month_df

# Function to find the heatmap
def heatmap(user, data):
    if(user != 'Overall'):
        data = data[data['User'] == user]

    # Get the period column, e.g., 8-9, 13-14, etc.
    period = []
    for hour in data['Hour']:
        if hour == 23:
            period.append(str(hour) + '-' + str(0))
        else:
            period.append(str(hour) + '-' + str(hour+1))

    data['Period'] = period
    # Make the date column
    data['Date'] = data['Day'].astype(str) + '-' + data['Month'].astype(str) + '-' + data['Year'].astype(str)
    data['Date'] = pd.to_datetime(data['Date'])
    data['Day name'] = data['Date'].dt.day_name()

    return data

# Function to find who uses vulgar words, from a list of vulgar words
def find_vulgar_user(data):
    user_list = data['User'].unique().tolist()

    vulg = open('vulgar_words.txt', 'r')
    vulgar_words = vulg.read().splitlines()

    vulg_count = []
    for user in user_list:
        vulg_count.append(data[data['User'] == user]['Message'].str.lower().str.contains('|'.join(vulgar_words)).sum())

    vulg_df = pd.DataFrame({'User':user_list, 'Vulgar word count':vulg_count})
    vulg_df = vulg_df[vulg_df['Vulgar word count'] != 0]
    vulg_df.sort_values('Vulgar word count', ascending=False, inplace=True)

    return vulg_df

# Function to find the frequency of vulgar words used
def find_vulgar_freq(data):
    vulg = open('vulgar_words.txt', 'r')
    vulgar_words = vulg.read().splitlines()

    vulg_count = []
    for word in vulgar_words:
        vulg_count.append(data['Message'].str.lower().str.contains(word).sum())

    vulg_df = pd.DataFrame({'Vulgar word':vulgar_words, 'Vulgar word count':vulg_count})
    vulg_df = vulg_df[vulg_df['Vulgar word count'] != 0]
    vulg_df.sort_values('Vulgar word count', ascending=False, inplace=True)

    return vulg_df
