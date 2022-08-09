import io

import emoji
import nltk

import streamlit as st
from langdetect import detect

from src.preprocessing import get_data_from_txt
from src.data import (get_basic_infos, get_maximal_silence_period,
                      get_mean_media_interval, get_mean_message_len,
                      get_moving_average_nb_message, get_number_of_message,
                      get_questions_by_name)
from src.viz import (plot_daily_data, plot_emoji_data, plot_hourly_data,
                     plot_monthly_data, plot_moving_nb_messages,
                     plot_moving_nb_messages_individuals,
                     plot_percentage_msg_emoji, plot_wordcloud)

# NLTK dependencies
nltk.download('punkt')
nltk.download('stopwords')

# Page configuration
st.set_page_config(layout="centered",
                   page_icon="💬",
                   page_title="Whatsapp Group Analyzer")
col1, col2, col3 = st.columns([1, 1, 1])
col2.image("./assets/whatsapp_logo.png", use_column_width=True)
st.markdown("<h1 style='text-align: center;'>Whatsapp Group Analyzer</h1>", unsafe_allow_html=True)


# Sidebar
st.sidebar.title("Whatsapp Group Analyzer")
st.sidebar.text(emoji.emojize("Created by Arnaud Trog."))

st.sidebar.write(emoji.emojize("Import a group conversation and analyze it with the power of Python & data viz !"
                              " Features included are : emoji analyzer, temporal analysis, user activities and much more."))

# Data configuration
option = st.sidebar.selectbox(
        'What type of date format ?',
        (emoji.emojize(f"{emoji.emojize(':France:')} : 01/02/2016 à 15:30"),
         emoji.emojize(f"{emoji.emojize(':United_States:')} : 02/01/16, 15:30"))
)

if option == emoji.emojize(f"{emoji.emojize(':France:')} : 01/02/2016 à 15:30"):# '01/02/2016 à 15:30':
    date_format = '%d/%m/%Y à %H:%M'
    header = r"(\d{2}/\d{2}/\d{4} à \d{2}:\d{2} - )"
elif option == emoji.emojize(f"{emoji.emojize(':United_States:')} : 02/01/16, 15:30"):# "02/01/16, 15:30":
    date_format = '%m/%d/%y, %H:%M'
    header = r"(\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2} - )"
else:
    pass

# Get raw data
uploaded_file = st.sidebar.file_uploader("Choose a Whatsapp group conversation")

# How to export conversation to analyze
with st.sidebar.expander(emoji.emojize(":red_question_mark: How to export WhatsApp chat")):
    """
    1. Open Whatsapp on your phone 
    2. Click on the desired conversation
    3. Open the menu with the three dots
    4. Click on «Export data» and select without media
    """
st.sidebar.write("")


### MAIN ###
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    txt_file = bytes_data.decode("utf-8")
    txt_file = io.StringIO(txt_file)
    data = get_data_from_txt(txt_file, header, date_format)
    detected_language = detect(" ".join(data["message"]))

    if detected_language == "fr":
        language = "french"
        media_message = "<Médias omis>"
    elif detected_language == "en":
        language = "english"
        media_message = "<Media omitted>"
    else:
        pass


    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overall statistics", "Emoji", "Temporal", "Activity", "Words"])

    with tab1:
        st.markdown(
            f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> {emoji.emojize('Overall statistics')} </p>",
            unsafe_allow_html=True)
        infos = get_basic_infos(data, media_message)
        st.write(emoji.emojize(f":play_button: Conversation starting from : {infos['start_date']}"))
        st.write(emoji.emojize(f":stop_button: Until to : {infos['end_date']}"))
        st.write(emoji.emojize(f":speaking_head: Number of participants : {infos['n_authors']}"))
        st.write(emoji.emojize(f":speech_balloon: Total number of messages : {infos['n_messages']}"))

        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> {emoji.emojize('Biggest questioner :thinking_face:')} </p>",
                unsafe_allow_html=True)
            questions = get_questions_by_name(data)
            first, second, third = list(questions.items())[:3]

            st.write(emoji.emojize(f":1st_place_medal: {first[0]} with {first[1]} questions"))
            st.write(emoji.emojize(f":2nd_place_medal: {second[0]} with {second[1]} questions"))
            st.write(emoji.emojize(f":3rd_place_medal: {third[0]} with {third[1]} questions"))

        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> {emoji.emojize('Most talkative :loudspeaker:')} </p>",
                unsafe_allow_html=True)
            msg_per_author = get_number_of_message(data)
            msg_len_per_author = get_mean_message_len(data)

            first, second, third = list(msg_per_author.items())[:3]
            st.write(emoji.emojize(f":1st_place_medal: {first[0]} with {first[1]} messages and an average message size of {int(msg_len_per_author[first[0]])} characters"))
            st.write(emoji.emojize(f":2nd_place_medal: {second[0]} with {second[1]} messages and an average message size of {int(msg_len_per_author[second[0]])} characters"))
            st.write(emoji.emojize(f":3rd_place_medal: {third[0]} with {third[1]} messages and an average message size of {int(msg_len_per_author[third[0]])} characters"))

        st.markdown('----')
        with st.container():
            st.markdown(f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> {emoji.emojize('Most silent :shushing_face:')} </p>", unsafe_allow_html=True)

            silence_per_author = get_maximal_silence_period(data)

            first, second, third = list(silence_per_author.items())[:3]
            st.write(emoji.emojize(
                f":1st_place_medal: {first[0]} with {first[1]} of silence."))
            st.write(emoji.emojize(
                f":2nd_place_medal: {second[0]} with {second[1]} of silence."))
            st.write(emoji.emojize(
                f":3rd_place_medal: {third[0]} with {third[1]} of silence."))

        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> {emoji.emojize('Most media sender :camera:')} </p>",
                unsafe_allow_html=True)

            media_intervals = get_mean_media_interval(data, media_message)

            first, second, third = list(media_intervals.items())[:3]
            st.write(emoji.emojize(
                f":1st_place_medal: {first[0]} with media sent every {first[1]}."))
            st.write(emoji.emojize(
                f":2nd_place_medal: {second[0]} with media sent every {second[1]}."))
            st.write(emoji.emojize(
                f":3rd_place_medal: {third[0]} with media sent every {third[1]}."))


    with tab2:
        st.header("Emoji analysis")
        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> Most used emoji in the conversation </p>",
                unsafe_allow_html=True)
            #st.write("Most used emoji in the conversation")
            fig = plot_emoji_data(data, show=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> Who uses emoji the most ? </p>",
                unsafe_allow_html=True)
            #st.write("Who uses emoji the most?")
            fig = plot_percentage_msg_emoji(data, show=False)
            st.pyplot(fig, use_container_width=True)

    with tab3:
        st.header("Temporal analysis")

        option = st.selectbox(
            'At which frequency do you want the analysis ?',
            ('Hourly', 'Daily', 'Monthly'))

        st.markdown('----')
        with st.container():

            st.info("The graph below was made with Plotly and is interactive. "
                    "You can single click on one member to remove him "
                    "or double click to see only this member. "
                    "The radius represents the percentage of message at this period.")

            if option == "Hourly":
                fig = plot_hourly_data(data, show=False)
                st.plotly_chart(fig, use_container_width=True)
            elif option == "Daily":
                fig = plot_daily_data(data, show=False)
                st.plotly_chart(fig, use_container_width=True)
            elif option == "Monthly":
                fig = plot_monthly_data(data, show=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("not yet implemented")

    with tab4:
        st.header("Activity analysis")

        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> Moving number of messages per week (global) </p>",
                unsafe_allow_html=True)
            data_tmp = get_moving_average_nb_message(data)
            fig = plot_moving_nb_messages(data_tmp, show=False)
            st.pyplot(fig, use_container_width=True)

        st.markdown('----')
        with st.container():
            st.markdown(
                f"<p style='text-align: center; font-size: 17px; font-weight: bold;'> Moving number of messages per week (individual) </p>",
                unsafe_allow_html=True)
            #st.write(emoji.emojize(":right_arrow: Moving sum number of messages per week (individual)"))
            fig = plot_moving_nb_messages_individuals(data, show=False)
            st.pyplot(fig, use_container_width=True)


    with tab5:
        st.header("Natural language analysis")
        #st.markdown('----')
        st.info("The graph below represents the most used words in the conversation."
                " The size of the words is proportional to its frequency after removing stop words"
                " (i.e. common / useless words).")
        fig = plot_wordcloud(data, language=language, show=False)
        st.pyplot(fig, use_container_width=True)
