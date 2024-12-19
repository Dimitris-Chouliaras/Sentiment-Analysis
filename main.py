from textblob import TextBlob
import pandas as pd
import streamlit as st
import io
import cleantext
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')


# Creating 2 functions
# 1st function using textblob library to do the sentiment analysis
# 2nd function using NLTK library to do the sentiment analysis


def get_response(selected_model, text, threshold):
    if selected_model == "TextBlob":
        blob = TextBlob(text)
        score = round(blob.sentiment.polarity, 2)
        subjectivity = round(blob.sentiment.subjectivity, 2)
        analysis = "Positive"
        if score < threshold:
            analysis = "Neutral"
        if score < -threshold:
            analysis = "Negative"
        return score, subjectivity, analysis
    if selected_model == "NLTK":
        nltk_analysis = SentimentIntensityAnalyzer().polarity_scores(text)
        score = round(nltk_analysis['compound'], 2)
        analysis = "Positive"
        if score < threshold:
            analysis = "Neutral"
        if score < -threshold:
            analysis = "Negative"
        return score, ":green[Not available with this model]", analysis


def main():
    threshold = 0
    # Starting with the header
    st.header('Sentiment Analysis')
    selected_threshold = st.selectbox("Select a threshold:", ["Default", "Neutral", "Pos-Neg"])
    if selected_threshold == "Default":
        threshold = 0.33
    elif selected_threshold == "Neutral":
        threshold = 0.66
    elif selected_threshold == "Pos-Neg":
        threshold = 0.10

    selected_model = st.selectbox("Select a model:", ["TextBlob", "NLTK"])
    # 1st we are going to develop a place that the user can insert his text and have a sentiment analysis
    with st.expander('Analyze Text'):
        text = st.text_input('Text here: ')
        if text:
            x, y, analysis = get_response(selected_model, text, threshold)
            st.write('Polarity: ', x)
            st.write('Subjectivity: ', y)
            st.write(f'The sentiment analysis of the text given is: {analysis}')
            st.write('')
            st.write(':red[*Range of Polarity: -1 to +1 (the range of expression from negative to positive)]')
            st.write(':red[*Range of Subjectivity: 0 to +1 (the range of personal opinions and feelings)]')
    # 2nd we are going to develop a place that the user can insert his text and have it cleaned from unnecessary words
        pre = st.text_input('Clean Text: ')
        if pre:
            st.write(cleantext.clean(pre, clean_all=False, extra_spaces=True, stopwords=True,
                                     lowercase=True, numbers=True, punct=True))
            st.write('')
            st.write(':red[Removing unnecessary words which have zero impact from the text given]')
    # 3rd we are going to develop a place that the user can upload a csv file and have a sentiment analysis
    with st.expander('Analyze Excel or CSV'):
        upl = st.file_uploader('Upload your file')
        if upl is not None:
            if upl.name.endswith('.csv'):   # making sure it's a csv file and then read it
                dataframe = pd.read_csv(upl)
            elif upl.name.endswith('.xlsx'):    # making sure it's a xlsx file and then read it
                dataframe = pd.read_excel(upl)
            else:
                st.write("Unsupported file format")   # stop when there is an unsupported file format
                st.stop()
            # Column selection to perform sentiment analysis
            columns = dataframe.columns.tolist()
            columns.insert(0, "Select Column")
            selected_column = st.selectbox('Select Column for Analysis:', columns)
            # Preview the uploaded file
            if dataframe is not None:
                st.subheader('Data Preview')
                results = []
                # adding 2 more columns 'score' and 'analysis' and preview the final product
                if selected_column != "Select Column":
                    for sentence in dataframe.get(selected_column):
                        score, _, analysis = get_response(selected_model, sentence, threshold)
                        results.append((sentence, score, analysis))
                    results_df = pd.DataFrame(results, columns=[selected_column, "Score", "Analysis"])
                    st.dataframe(results_df)

                    # convert pandas dataframe to xlsx file
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        results_df.to_excel(writer, index=False, sheet_name='Sheet1')
                    excel_data = excel_buffer.getvalue()
                    # making a download button so the user can download the analyzed data in a xlsx file
                    st.download_button(
                        label="Download data as Excel",
                        data=excel_data,
                        file_name='analyzed_data.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                else:
                    st.dataframe(dataframe)

    # End with a footer - Always displayed and fixed in the bottom of the page
    st.markdown("""
    <style>
    /* Ensure that the body takes up the full height */
    body {
        display: flex;
        flex-direction: column;
        height: 100vh;
        margin: 0;
    }

    /* Allow content to expand and take up available space */
    .content {
        flex-grow: 1;
        overflow-y: auto;
    }

    /* Style the footer */
    .footer {
        width: 100%;
        text-align: center;
        color: white;
        background-color: #000000;
        padding: 10px 0;
        font-family: Arial, sans-serif;
        font-size: 14px;
    }

    .footer a {
        color: white;
        font-size: 18px;
        text-decoration: none;
        margin: 0 15px;
    }
    
    .footer a:hover {
        color: #00aaff;
    }

    /* Footer links container */
    .footer-links {
        margin-top: 10px;
    }

    /* Style for individual social icons */
    .footer-links a {
        color: white;
        font-size: 24px;
        margin: 0 15px;
    }

    .footer-links a:hover {
        color: #00aaff;
    }
    </style>
    <div class="footer">
        <p>Developed by Chouliaras Dimitrios<br>UTH Thessaly</p>
        <div>
            <a href="https://www.linkedin.com/in/dimitrios-chouliaras/" target="_blank">
                <i class="fab fa-linkedin"></i> LinkedIn
            </a>
            |
            <a href="https://github.com/Dimitris-Chouliaras" target="_blank">
                <i class="fab fa-github"></i> GitHub
            </a>
        </div>
    </div>

    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">
    """, unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()
