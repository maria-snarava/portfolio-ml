import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import yfinance as yf
import io
import requests

#URL used for streamlit cloud
DATA_URL_1 = "https://raw.githubusercontent.com/maria-snarava/portfolio-ml/main/Dashboard/data/prepared_data_1.csv"
DATA_URL_2 = "https://raw.githubusercontent.com/maria-snarava/portfolio-ml/main/Dashboard/data/prepared_data_2.csv"
#to read local files use this path
DATA_PATH_1 = Path('data/prepared_data_1.csv')
DATA_PATH_2 = Path('data/prepared_data_2.csv')
COMPANY = ('apple', 'Google Inc', 'Amazon.com', 'Tesla Inc', 'Microsoft')
TICKER = ('AAPL', 'GOOG', 'AMZN', 'TSLA', 'MSFT')
def get_random_tweet():
    return company_data.query('sentiment == @random_tweet_sentiment')[["body"]].sample(n=1).iat[0, 0]

def get_top5_tweets(top_tweet_sentiment):
    if top_tweet_sentiment == 'all sentiments':
        return company_data.sort_values('engagement', ascending=False).head()
    else:
        return company_data.query('sentiment == @top_tweet_sentiment').sort_values('engagement', ascending=False).head()

def get_word_cloud(sentiment_for_word_cloud):
    # use only 100 random tweets for cloud
    if sentiment_for_word_cloud == 'all sentiments':
        df = company_data.sample(n=100)
    else:
        df = company_data.query('sentiment == @sentiment_for_word_cloud').sample(n=100)

    words = ' '.join(df['body'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith(
        '@') and 'URL' not in word and 'REMOVED' not in word and word.upper() not in TICKER])
    return WordCloud(stopwords=STOPWORDS, background_color='white', height=640, width=800).generate(
        processed_words)

def get_tweets_count(data):
    company_count = data['company_name'].value_counts()
    return pd.DataFrame({'Company': company_count.index, 'Tweets': company_count.values})

def get_engagement_count(data):
    engagement_count = data.groupby('company_name').engagement.sum()
    return pd.DataFrame({'Company': engagement_count.index, 'Engagement': engagement_count.values})

def get_sentiment_count(company_data):
    sentiment_count = company_data['sentiment'].value_counts()
    return pd.DataFrame({'Sentiment': sentiment_count.index, 'Tweets': sentiment_count.values})

@st.cache_data(persist=True)
def load_data():
    s = requests.get(DATA_URL_1).content
    data_1 = pd.read_csv(io.StringIO(s.decode('utf-8')))
    s = requests.get(DATA_URL_2).content
    data_2 = pd.read_csv(io.StringIO(s.decode('utf-8')))
    #Use this code to read from the local files
    #data_1 = pd.read_csv(DATA_PATH_1)
    #data_2 =  pd.read_csv(DATA_PATH_2)
    data = pd.concat([data_1, data_2])

    return data

def get_timeline_by_company(df):
    timeline = df.groupby(['date', 'company_name']).size().reset_index()
    timeline_df = pd.DataFrame({
        'date': timeline.date.unique(),
        'apple': list(timeline[timeline['company_name'] == 'apple'][0]),
        'Google Inc': list(timeline[timeline['company_name'] == 'Google Inc'][0]),
        'Amazon.com': list(timeline[timeline['company_name'] == 'Amazon.com'][0]),
        'Tesla Inc': list(timeline[timeline['company_name'] == 'Tesla Inc'][0]),
        'Microsoft': list(timeline[timeline['company_name'] == 'Microsoft'][0])
    })

    return timeline_df

def get_timeline_engagement(df):
    timeline = df.groupby(['date', 'company_name']).engagement.sum().reset_index()
    timeline_df = pd.DataFrame({
        'date': timeline.date.unique(),
        'apple': list(timeline[timeline['company_name'] == 'apple']['engagement']),
        'Google Inc': list(timeline[timeline['company_name'] == 'Google Inc']['engagement']),
        'Amazon.com': list(timeline[timeline['company_name'] == 'Amazon.com']['engagement']),
        'Tesla Inc': list(timeline[timeline['company_name'] == 'Tesla Inc']['engagement']),
        'Microsoft': list(timeline[timeline['company_name'] == 'Microsoft']['engagement'])
    })

    return timeline_df
def get_timeline_by_sentiment(df):
    timeline = df.groupby(['date', 'sentiment']).size().reset_index()
    for date in list(timeline.date.unique()):
        if 'negative' not in list(timeline[timeline['date'] == date].sentiment):
            row = {'date': date, 'sentiment': 'negative', 0: 0}
            timeline.loc[len(timeline)] = row
    timeline = timeline.sort_values(by='date')

    timeline_df = pd.DataFrame({
        'date': timeline.date.unique(),
        'neutral': list(timeline[timeline['sentiment'] == 'neutral'][0]),
        'positive': list(timeline[timeline['sentiment'] == 'positive'][0]),
        'negative': list(timeline[timeline['sentiment'] == 'negative'][0])
    })

    return timeline_df


def get_timeline_by_sentiment_vs_stock(df):
    timeline = df.groupby(['date', 'sentiment']).size().reset_index()
    timeline_for_all = df.groupby(['date']).size().reset_index()

    for date in list(timeline.date.unique()):
        if 'negative' not in list(timeline[timeline['date'] == date].sentiment):
            row = {'date': date, 'sentiment': 'negative', 0: 0}
            timeline.loc[len(timeline)] = row

    timeline = timeline.sort_values(by='date')
    timeline_df = pd.DataFrame({
        'date':  timeline.date.unique(),
        'all_tweets': list(timeline_for_all[0]),
        'neutral': list(timeline[timeline['sentiment'] == 'neutral'][0]),
        'negative': list(timeline[timeline['sentiment'] == 'negative'][0]),
        'positive': list(timeline[timeline['sentiment'] == 'positive'][0])

    }).set_index('date')

    stock = yf.Ticker(TICKER[COMPANY.index(selected_company)])
    stock_df = stock.history(period="1d", start=df['date'].min(), end=df['date'].max())

    stock_df['date'] = pd.to_datetime(stock_df.index, unit='s').date
    stock_df = stock_df.astype({"date": str})
    stock_df = stock_df.set_index('date')
    stock_df = stock_df.join(timeline_df).reset_index()
    if selected_company == 'Tesla Inc':
        coff = 20
    elif selected_company == 'Microsoft':
        coff = 1
    else:
        coff = 5
    stock_df[f'stock_price_x{coff}'] = stock_df['Close'] * coff

    return stock_df[['date', f'stock_price_x{coff}', 'neutral', 'all_tweets', 'negative',  'positive']]


data = load_data()

st.title('Sentimental analysis of Tweets about major NASDAQ-listed companies in 2019 year')
st.markdown(':gray[This project uses a dataset [Tweets about the Top Companies from 2015 to 2020](https://www.kaggle.com/datasets/omermetinn/tweets-about-the-top-companies-from-2015-to-2020/data), featuring tweets related to major NASDAQ-listed companies, that was posted between 01-01-2019 and 31-12-2019. Sentiment analysis was performed using the NLTK library, along with a financial dictionary to better capture the nuances of financial terms. Engagement metrics were computed based on the number of likes, retweets, and comments each tweet received. You can find the preprocessing steps and code on the project’s [GitHub repository](https://github.com/maria-snarava/portfolio-ml).]')

#Part 1: Visualization of All Tweets
st.header(':green[Part 1: All tweets analysis]')
st.sidebar.header(':green[Part 1: All tweets analysis]')
select = st.sidebar.selectbox('Visualization type', ['Histogram', 'Pie chart', 'Timeline'])
tweet_count = get_tweets_count(data)
st.markdown('### :blue[Number of tweets by company]')
st.markdown(''':gray[This section allows you to explore the overall distribution of tweets through various graph types. A drop-down menu on sidebord offers three options for visualizing the data:]

:gray[**Histogram:** Shows the distribution of tweets over companies.]

:gray[**Pie chart:** Displays the proportions of different sentiment categories.]

:gray[**Timeline:** Tracks the volume of tweets over time. You can enable/disable information about every company by clicking on it's name on the right.]''')
if select == "Pie chart":
    tweets_by_company = px.pie(tweet_count, names = 'Company', values = 'Tweets')
if select == "Timeline":
    timeline = get_timeline_by_company(data)
    tweets_by_company = px.line(timeline, x='date', y=timeline.columns[1:7])
if select == "Histogram":
    tweets_by_company = px.bar(tweet_count, x='Company', y='Tweets', color='Tweets', height=500)

st.plotly_chart(tweets_by_company)

st.markdown('### :blue[Engagement]')
st.markdown('''This plot illustrates the Engagement Metric, which helps understand how much attention received tweets about every company.''')
st.markdown(':gray[More likes, retweets and comments - more engagement points. Retweet = 2 like, Comment = 3 like]')
engagement_count = get_engagement_count(data)
if select == "Histogram":
    engagement_fig = px.bar(engagement_count, x='Company', y='Engagement', color='Engagement', height=500)
if select == 'Pie chart':
    engagement_fig = px.pie(engagement_count, names = 'Company', values = 'Engagement')
if select == "Timeline":
    timeline = get_timeline_engagement(data)
    engagement_fig = px.line(timeline, x='date', y=timeline.columns[1:7])
st.plotly_chart(engagement_fig)


# Part 2: Breakdown tweets by sentiment
st.sidebar.subheader(':blue[Breakdown of tweets by sentiment]')
choice = st.sidebar.multiselect('Pick Company', COMPANY, default = COMPANY)

if len(choice) > 0:
    st.markdown('### :blue[Breakdown of tweets by sentiment]')
    st.markdown(''':gray[This part provides a deeper look into how tweets are distributed across different sentiments. You can select multiple company names on the sidebar to compare sentiment breakdowns by company, visualizing which companies received more attention.]''')
    choiced_data = data[data.company_name.isin(choice)]
    fig_choice = px.histogram(choiced_data, x='company_name', y='sentiment', histfunc='count',
                                  color='sentiment', facet_col='sentiment',
                                  height=600, width=800)
    st.plotly_chart(fig_choice)

#Part 3: Select company
st.markdown("________________")
st.sidebar.header(':green[Part 2: Select a company for detailed analysis]')
selected_company = st.sidebar.radio('Company', COMPANY)
company_data = data.query('company_name == @selected_company')
st.header(f":green[Part 2: Detailed analysis for {selected_company}]")
st.markdown(''':gray[Here, you can focus on a specific company by selecting its name through a radio button. The selected company will be used for further detailed sentiment analysis in the upcoming sections.]''')

#Part 4: Sentiment
if st.sidebar.checkbox(f":blue[Show Number of Tweets by Sentiment for the {selected_company}]", True):
    select_by_company = st.sidebar.selectbox('Visualization type ', ['Histogram', 'Pie chart', 'Timeline'])
    sentiment_count = get_sentiment_count(company_data)
    st.markdown(f'### :blue[Number of Tweets by Sentiment for the {selected_company}]' )
    st.markdown(''':gray[This section offers insights into the number of tweets categorized by sentiment for the chosen company. You can select a plot type from the drop-down menu, choosing between:]

:gray[**Histogram:** Displays the count of tweets per sentiment.]

:gray[**Pie chart:** Shows the sentiment proportions.]

:gray[**Timeline:** Reveals how sentiment trends evolve over time.]''')
    if select_by_company == "Timeline":
        timeline_by_sentiment = get_timeline_by_sentiment(company_data)
        company_tweets_by_sentiment = px.line(timeline_by_sentiment, x='date', y=timeline_by_sentiment.columns[1:4])
    if select_by_company == "Pie chart":
        company_tweets_by_sentiment = px.pie(sentiment_count, names = 'Sentiment', values = 'Tweets')
    if select_by_company == "Histogram":
        company_tweets_by_sentiment = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=500)
    st.plotly_chart(company_tweets_by_sentiment)

#Part 5:
if st.sidebar.checkbox(f":blue[Show Number of Tweets by Sentiment vs. Stock Price]", True):
    sentiment_count = get_sentiment_count(company_data)
    st.markdown(f'### :blue[Number of tweets about {selected_company} by sentiment vs stock price]' )
    st.markdown(''':gray[In this timeline plot, you can examine the correlation between tweet sentiment and the company's stock price. The plot shows the number of tweets for each sentiment alongside the stock price movements, providing insights into how market sentiment may align with stock performance. You can enable/disable each line by clicking on it's name on the right.]''')

    timeline_vs_stock = get_timeline_by_sentiment_vs_stock(company_data)
    company_tweets_by_sentiment_vs_stock = px.line(timeline_vs_stock, x='date', y=timeline_vs_stock.columns[1:6])
    st.plotly_chart(company_tweets_by_sentiment_vs_stock)
#Part 6: Word Cloud
if st.sidebar.checkbox(":blue[Show Word cloud]",True):
    sentiment_for_word_cloud = st.sidebar.radio('Word Cloud Sentiment', ('all sentiments', 'positive', 'neutral', 'negative'))
    st.markdown(f'### :blue[{sentiment_for_word_cloud} word cloud for {selected_company}]')
    st.markdown(''':gray[This section generates a word cloud for the selected company, allowing you to visualize the most common words used in tweets. You can choose the sentiment type on the sidebar - All Sentiments, Positive, Neutral, or Negative — to see the keywords associated with each sentiment.]''')
    word_cloud = get_word_cloud(sentiment_for_word_cloud)
    plt.imshow(word_cloud)
    plt.axis('off')
    st.pyplot(plt)

#Part 7: Random tweet
if st.sidebar.checkbox(f":blue[Show a Random Tweet About {selected_company}]", True):
    random_tweet_sentiment = st.sidebar.radio('A Random Tweet Sentiment', ('positive', 'neutral', 'negative'))
    st.markdown(f'### :blue[A Random {random_tweet_sentiment} Tweet About {selected_company}]')
    if st.button('Show next random tweet'):
        st.markdown(get_random_tweet())
    else:
        st.markdown(get_random_tweet())

#Part 8: Top 5 most engaging tweets
if st.sidebar.checkbox(":blue[Show top 5 Most Engaging Tweets]", True):
    top_tweet_sentiment = st.sidebar.radio(' Most Engaging Tweets Sentiment', ('all sentiments', 'positive', 'neutral', 'negative'))
    st.markdown(f'### :blue[Top 5 Most Engaging Tweets About {selected_company} ({top_tweet_sentiment})]')
    st.markdown(''':gray[You can view the top 5 tweets with the highest engagement for the selected company. There is an option to filter these tweets by sentiment type using a radio button, with the choices being All Sentiments, Positive, Neutral, or Negative.]''')
    top5_tweets = get_top5_tweets(top_tweet_sentiment)
    for index, tweet in top5_tweets.iterrows():
        st.markdown(f"**:blue[Date: {tweet['date']}, Engagement: {tweet['engagement']}, Sentiment: {tweet['sentiment']}, Tweet:]** ")
        st.markdown(f"{tweet['body']} ")

