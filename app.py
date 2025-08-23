import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import preprocessor as pp
import helper as hp
import seaborn as sns

#----------- Titlebar and Sidebar -------------
st.set_page_config(page_title='WhatsApp Chat Analyzer', page_icon='Wtsp.png', initial_sidebar_state='auto')
st.sidebar.image('Wtsp.png', width=250)

#----------- File is uploaded -------------
upload_file = st.sidebar.file_uploader("Upload your WhatsApp Chat file with the name and format as - {Chat with <name>.txt}:")
if upload_file is not None:
    #------------- Naming the file -------------
    data = upload_file.getvalue().decode("utf-8")
    filename = upload_file.name
    filename = filename.split('.')[0]
    recipient_name = filename.split('with ')[1]
    st.title("Chat Analysis for : \"{}\"".format(recipient_name))

    #------------- Preprocess the data -------------
    pdf = pp.preprocess(data, recipient_name)

    #---------------- Unique users list ---------------
    unique_users = pdf['User'].unique().tolist()
    unique_users.sort()
    unique_users.insert(0, 'Overall')

    user = st.sidebar.selectbox("Select User:", unique_users)
    
    menu = st.selectbox(
        'Select an option:',
        ('The chat', 'General Statistics', 'See Wordcloud', 'Most Active Users', 'Busiest days/months', 
         'Most frequently used words', 'Emoji Analysis', 'Month/Daily-wise chat Analysis', 'Heatmap', 'Vulgar chat analysis')
    )

    #------------- The chat -------------
    if menu == 'The chat':
        st.title("The chat")
        if user == 'Overall':
            st.dataframe(pdf)
        else:
            st.dataframe(pdf[pdf['User'] == user])
            
    #------------- Wordcloud -------------
    if menu == 'See Wordcloud':
        wc = hp.create_cloud(user, pdf)
        fig = plt.figure(figsize=(20,20))
        plt.imshow(wc)
        plt.axis('off')
        st.pyplot(fig)
    
        #----------- Fetch the user selected stats -----------
    if menu == 'General Statistics':
        st.title("General Statistics")
        n, words, m, url = hp.fetch_stats(user, pdf)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header("Total Messages:")
            st.title(n)
        with col2:
            st.header("Total Words:")
            st.title(len(words))
        with col3:
            st.header("Total Media:")
            st.title(m)
        
        st.header("URLs in the chat:")
        st.markdown('**Total URLs shared:** {}'.format(len(url)))
        st.markdown('**URL List:**')
        st.dataframe(url)

    #------------- Finding the busiest users in the group -----------
    if menu == 'Most Active Users':
        if user == 'Overall':
            st.title("Most Active Users")
            value, pu = hp.busy_users(pdf)
            pu = pd.DataFrame(pu)
            pu.rename(columns={'count':'%_of_msg', '%_of_msg': 'User'}, inplace=True)
            
            # remove group_notification from the dataframe
            st.markdown('**Most active user:** {}'.format(value.index[0]))
            st.markdown('**Least active user:** {}'.format(value.index[-1]))

            col1, col2 = st.columns(2)
            value = pd.DataFrame(value).reset_index()
            value.rename(columns={'index':'User', 'User':'Message Count', }, inplace=True)

            with col1:
                st.dataframe(value)
            with col2:
                fig = px.pie(pu, values='%_of_msg', names='User', width=400, height=400)
                st.plotly_chart(fig)
        
        else:
            st.header("NOTE: This feature is only available for Group chats.")

    #------------- Finding the busiest days in the group -----------
    if menu == 'Busiest days/months':
        st.title("Busiest days")
        day_df, month_df = hp.busy_days_months(user, pdf)

        day_df.rename(columns={'Message Count':'Day', 'count':'Message Count'}, inplace=True)
        month_df.rename(columns={'Message Count':'Month', 'count':'Message Count'}, inplace=True)
        st.markdown('**Most busy day:** {}'.format(day_df['Day'].iloc[0]))
        st.markdown('**Least busy day:** {}'.format(day_df['Day'].iloc[-1]))

        col1, col2 = st.columns(2)
        with col1:
            st.header("Messages sent:")
            st.dataframe(day_df)
        with col2:
            fig = px.bar(day_df, x='Day', y='Message Count', width=400, height=400)
            st.plotly_chart(fig)

        st.title("Busiest months")
        st.markdown('**Most busy month:** {}'.format(month_df['Month'].iloc[0]))
        st.markdown('**Least busy month:** {}'.format(month_df['Month'].iloc[-1]))

        col1, col2 = st.columns(2)
        with col1:
            st.header("Messages sent:")
            st.dataframe(month_df)
        with col2:
            fig = px.bar(month_df, x='Month', y='Message Count', width=400, height=400)
            st.plotly_chart(fig)

    #--------------- Most frequently used words ----------------
    if menu == 'Most frequently used words':
        most_used = hp.find_common_words(user, pdf)
        st.title("Most frequently used words")
        st.dataframe(pdf)
        st.table(most_used)
        # Plot it in a horizontal bar chart
        fig = px.bar(most_used.head(10), x='Count', y='Word', orientation='h', width=400, height=400)
        st.plotly_chart(fig)

    #------------------ Emoji Analysis ------------------
    if menu == 'Emoji Analysis':
        emoji_df = hp.emoji_analysis(user, pdf)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Emojis used:")
            st.dataframe(emoji_df)
        with col2:
            st.header("Top 10 emojis:")
            fig = px.pie(emoji_df.head(10), values='Count', names='Emoji', width=400, height=400)
            st.plotly_chart(fig)

    #------------------ Month/Daily-wise chat Analysis ------------------
    if menu == 'Month/Daily-wise chat Analysis':
        month_df = hp.monthly_analysis(user, pdf)
        st.title("Month-wise chat Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Messages sent:")
            st.dataframe(month_df.drop('mm/yyyy', axis=1))
        with col2:
            fig = px.line(month_df, x='mm/yyyy', y='Message', width=400, height=400)
            #update xlabel and ylabel
            fig.update_xaxes(title_text='Month/Year')
            fig.update_yaxes(title_text='Message Count')
            #update tickangle
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)

        st.title("Daily chat Analysis")
        daily_df = hp.daily_analysis(user, pdf)

        col1, col2 = st.columns(2)
        with col1:
            st.header("Messages sent:")
            st.dataframe(daily_df)
        with col2:
            fig = px.line(daily_df, x='Date', y='Message', width=400, height=400)
            #update xlabel and ylabel
            fig.update_xaxes(title_text='Date')
            fig.update_yaxes(title_text='Message Count')
            #update tickangle
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)

    #------------------ Heatmap ------------------
    if menu == 'Heatmap':
        st.title("Heatmap")
        hmap_data = hp.heatmap(user, pdf)
        fig = sns.heatmap(hmap_data.pivot_table(index='Day name', columns='Period', values='Message', aggfunc='count').fillna(0))
        # Update the x and y labels
        fig.set(xlabel='Hour-wise (24 hr. format)', ylabel='')
        sns.set(rc={'figure.figsize':(15, 10)})
        st.pyplot(fig.get_figure())

    #------------------ Vulgar chat analysis ------------------
    if menu == 'Vulgar chat analysis':
        # For the overall chat
        if user == 'Overall':
            st.title("Vulgar chat analysis")
            vulgar = hp.find_vulgar_user(pdf)
            vulgar_freq = hp.find_vulgar_freq(pdf)

            if vulgar.empty:
                st.markdown('**No vulgar words used in the chat!**')
            else:
                st.markdown('**Total vulgar words used:** {}'.format(vulgar['Vulgar word count'].sum()))
                st.markdown('**Most frequent vulgar word user:** {}'.format(vulgar['User'].iloc[0]))
                st.markdown('**Least frequent vulgar word user:** {}'.format(vulgar['User'].iloc[-1]))
                st.markdown('**Most frequent vulgar word:** {}'.format(vulgar_freq['Vulgar word'].iloc[0]))

                col1, col2 = st.columns(2)
                with col1:
                    st.header("Vulgar word users :")
                    st.dataframe(vulgar)

                with col2:
                    st.header(" ")
                    fig = px.bar(vulgar, x='User', y='Vulgar word count', width=400, height=400)
                    st.plotly_chart(fig)

                c1, c2 = st.columns(2)
                with c1:
                    st.header("Vulgar words used:")
                    st.dataframe(vulgar_freq)
                with c2:
                    st.header(" ")
                    fig = px.pie(vulgar_freq.head(10), values='Vulgar word count', names='Vulgar word', width=400, height=400)
                    st.plotly_chart(fig)

        # For a particular user
        else:
            st.header("SORRY!!! This feature is not available for individuals.")
            st.markdown("**Please select 'Overall' from the sidebar.**")

else:
    st.title("Whats Insight")
    st.markdown("Upload chat to get started! :sparkles:")

# Run the app
if __name__ == "__main__":
    st.markdown("With :heart: by *Sourav Chakraborty*")



