# Whats-Insight

### Introduction
An attempt to develop a utility application that serves as a versatile tool for transforming raw chat data into meaningful insights, enabling users to make informed decisions, enhance communication, and gain a better understanding of their WhatsApp conversations. It caters to both individuals as well as groups, for making any chat analysis. It offers several key functions, including message frequency analysis, sentiment analysis, tracking participant activity, evaluating media sharing statistics, and more. These features provide users with a comprehensive understanding of their messaging habits, the most active participants in group chats, trends in sentiment over time, and commonly used words and emojis. Also, we have further extended our application for detecting vulgar and offensive words used in chats, their frequency, and others.

### Modules
#### 1.	Data Collection and Data Preprocessing:
Data Collection: This module involves gathering the WhatsApp chat data for analysis. We can collect this data by exporting chat conversations from the WhatsApp application or using third-party tools if necessary.
Data Preprocessing: In this step, we clean and prepare the data for analysis. It includes removing irrelevant information, handling missing data, and ensuring the data is in a suitable format for further analysis.

#### 2.	Sentiment Analysis:
Sentiment Analysis: This module focuses on determining the emotional tone of the chat messages. It can be done using Natural Language Processing (NLP) techniques. We'll classify messages as positive, negative, or neutral to gauge the overall sentiment of the chat.

#### 3.	Text Tokenization:
Text Tokenization: Tokenization is the process of breaking down text into individual words or tokens. This module is essential for various aspects of analysis, including word frequency, user behavior, and summarization.

#### 4.	User Behavior Analysis:
User Behavior Analysis: This module involves studying how users interact within the WhatsApp chat. We can analyze message frequency, response times, most active users, and user engagement patterns.
Metrics and Analysis Methods: Detail the specific metrics we'll be measuring and the methods we'll use to analyze user behavior. We might consider using Python for data analysis and visualization.

#### 5. Summarization:
Summarization: In this module, we can generate a summary of the WhatsApp chat. This could be a summary of the entire conversation or summaries for specific sections or topics within the chat.
Summarization Techniques: Describe the techniques we'll use for summarization, such as extractive or abstractive summarization, and the libraries or models you'll implement. 

### Files
* preprocessor.py - takes the text file as input and preprocesses the data in our required format, identifies the users in the chat and their messages, etc.
* helper.py - it contains the functionality of all the modules that our app performs: chat statistics, wordcloud, emoji analysis, frequent words, vulgar word analysis, etc.
* app.py - the user interacts using this. It has the code for the entire frontend, developed using Python's frontend framework Streamlit
