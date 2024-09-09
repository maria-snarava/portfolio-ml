# Tweet Sentiment Analysis Dashboard for Top Companies 2019

## Project Overview

This project is a interactive dashboard for sentiment analysis of tweets about the top companies in 2019. The dashboard is built using Streamlit and Python, leveraging skills learned from the Coursera course ["Create Interactive Dashboards with Streamlit and Python"](https://www.coursera.org/projects/interactive-dashboards-streamlit-python).

## Data Source

The dataset used in this project is sourced from Kaggle and contains tweets about top companies from 2015 to 2020 years. It contains over 4 million unique tweets with their information such as tweet id, author of the tweet, post date, the text body of the tweet, and the number of comments, likes, and retweets of tweets matched with the related company. In my project I used only 2019's year tweets.

[Tweets about the Top Companies from 2015 to 2020](https://www.kaggle.com/datasets/omermetinn/tweets-about-the-top-companies-from-2015-to-2020/data)

## Features

- Sentiment analysis of tweets
- Interactive visualizations
- Company-wise sentiment breakdown
- Trend analysis over time

## Technologies Used

- Python
- Streamlit
- Pandas
- NLTK (for sentiment analysis)
- Plotly Express (for interactive charts)
- Wordcloud and Matplotlib Pyplot for words cloud visualization

## Setup and Installation

1. Clone the repository
   ```
   git clone git@github.com:maria-snarava/portfolio-ml.git
   ```

2. Navigate to the project directory
   ```
   cd Dashbord
   ```

3. Install the required packages
   ```
   pip install -r requirements.txt
   ```

4. Run the Streamlit app
   ```
   streamlit run app.py
   ```

## Usage

After running the app, navigate to the local URL provided by Streamlit (typically `http://localhost:8501`). Use the sidebar to interact with different features of the dashboard.

## Project Structure

```
├── README.md
├── app.py
├── requirements.txt
├── data/
│   └── prepared_data.csv
├── src/
│   ├── data_processing.py
```

## Future Improvements

- Add more advanced NLP techniques
- Implement real-time tweet fetching
- Enhance UI/UX with more interactive elements

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/maria-snarava/portfolio-ml/issues) if you want to contribute.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). This means:

You are free to:

 - Share — copy and redistribute the material in any medium or format
 - Adapt — remix, transform, and build upon the material


Under the following terms:

 - Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
 - NonCommercial — You may not use the material for commercial purposes.

For more details, please see the full license text.