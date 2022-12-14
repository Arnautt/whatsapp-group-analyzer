import os

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from nltk import word_tokenize
from nltk.corpus import stopwords
from PIL import Image
from wordcloud import WordCloud

from .data import *


def plot_messages_per_day(data, show=True):
    """
    Plot the number of message in a conversation for each day

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    msg_per_day = get_nb_message_per_day(data)
    plt.style.use("seaborn-bright")
    plt.figure(figsize=(14, 5))
    sns.lineplot(data=msg_per_day, x="day", y="date")
    plt.ylabel("number of message")
    plt.xlabel("day")
    if show:
        plt.show()
    else:
        fig = plt.gcf()
        return fig


def plot_moving_nb_messages(data, show=True):
    """
    Plot the moving number of message for a week

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    plt.figure(figsize=(14, 5))
    sns.lineplot(data=data, x="day", y="date")
    plt.ylabel("weekly moving number of message")
    plt.xlabel("date")
    if show:
        plt.show()
    else:
        fig = plt.gcf()
        return fig


def plot_moving_nb_messages_individuals(data, show=True):
    """
    Plot the moving number of message for a week for each participant in the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    authors = data["author"].unique()
    plt.figure(figsize=(14, 5))
    plt.style.use("seaborn-bright")

    for author in authors:
        data_author = data[data["author"] == author]
        tmp = get_moving_average_nb_message(data_author)
        sns.lineplot(data=tmp, x="day", y="date", label=author)

    plt.ylabel("moving average number of message")
    plt.xlabel("date")
    plt.legend()
    if show:
        plt.show()
    else:
        fig = plt.gcf()
        return fig


def plot_emoji_data(data, show=True):
    """
    Plot the percentage of emoji utilisation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    tmp = get_emoji_counter(data)
    fig = px.sunburst(tmp,
                      path=['emoji', 'author'],
                      values='count')
    fig.update_traces(textinfo="label+percent parent")
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
    )
    if show:
        fig.show()
    else:
        return fig


def plot_hourly_data(data, show=True):
    """
    Plot the percentage of message in each hour for each participant

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    data_copy = get_hourly_data(data)

    categories = [str(c) + "h" for c in data_copy.columns]
    fig = go.Figure()

    for _, row in data_copy.iterrows():
        author = row.name[-1]
        values = row.values
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=author
        ))

    fig.update_polars(angularaxis_type="category",
                      bgcolor="rgba(223, 223, 223, 0)")

    img = Image.open("./assets/clock.png")
    fig.add_layout_image(
        dict(
            source=img,
            xref="paper",
            yref="paper",
            x=.5,
            y=.5,
            xanchor="center",
            yanchor="middle",
            sizing="contain",
            opacity=0.9,
            sizex=1.7,
            sizey=1.7,
        )
    )
    fig.update_layout(template="plotly_white",
                      polar_angularaxis_showticklabels=False)

    if show:
        fig.show()
    else:
        return fig


def plot_daily_data(data, show=True):
    """
    Plot the percentage of message for each day for each participant

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    data_copy = get_daily_data(data)

    categories = [str(c) for c in data_copy.columns]
    fig = go.Figure()

    for _, row in data_copy.iterrows():
        author = row.name[-1]
        values = row.values
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=author
        ))

    if show:
        fig.show()
    else:
        return fig


def plot_monthly_data(data, show=True):
    """
    Plot the percentage of message for each month, for each participant

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    data_copy = get_monthly_data(data)

    categories = [str(c) for c in data_copy.columns]
    fig = go.Figure()

    for _, row in data_copy.iterrows():
        author = row.name[-1]
        values = row.values
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=author
        ))

    if show:
        fig.show()
    else:
        return fig


def plot_percentage_msg_emoji(data, show=True):
    """
    For each participant, plot the percentage of message with one or more emoji

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    show: bool
        SHow figure if True else return figure object
    """
    # Get data as dataframe with 3 columns (name, with emoji, no emoji)
    msg_with_emoji = percentage_msg_with_emoji(data)
    df = pd.DataFrame()
    df["name"] = msg_with_emoji.keys()
    df["with_emoji"] = msg_with_emoji.values()
    df["no_emoji"] = 1 - df["with_emoji"]

    # Stacked bar plot
    ax = df.plot(kind='bar',
                 stacked=True,
                 colormap="tab20c",
                 figsize=(10, 6),
                 title="Percentage of message with emoji",
                 ylabel="percentage",
                 rot=45)

    ax.set_xticklabels(df["name"].to_list())

    # Add percentage annotations
    for x, y in enumerate(df["with_emoji"]):
        y_offset = 0.05 if y != 0 else -0.02
        plt.text(x - 0.14, y - y_offset,
                 f"{round(y * 100, 1)}%", weight='bold')

    if show:
        plt.show()
    else:
        fig = plt.gcf()
        return fig


def plot_wordcloud(data, language="french", show=True):
    """
    Wordcloud for the most used words in the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    language: str
        Language used in the conversation
    show: bool
        SHow figure if True else return figure object
    """
    # Get tokens without stop words
    all_msg = " ".join(data["message"])
    tokens = word_tokenize(all_msg)
    filtered_tokens = [
        word for word in tokens if word not in stopwords.words(language)]
    filtered_tokens = " ".join(filtered_tokens)

    # Plot word cloud
    mask = np.array(Image.open("./assets/conv.jpg"))
    cloud = WordCloud(background_color='white',
                      collocations=False,
                      max_words=100,
                      mask=mask,
                      )

    cloud.generate(filtered_tokens)

    plt.figure(figsize=(18, 8))
    plt.imshow(cloud, interpolation='bilinear')
    plt.axis('off')

    # Show or return
    if show:
        plt.show()
    else:
        fig = plt.gcf()
        return fig
