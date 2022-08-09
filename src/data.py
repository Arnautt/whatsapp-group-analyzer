from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from emoji import emoji_count


def get_basic_infos(data, media_message):
    """
    Basic infos of the conversation dataframe

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    media_message: str
        Message value when a media is omitted (language dependant)

    Returns
    -------
    result: dict
        Basic statistics of the conversation
    """
    result = {}
    result["start_date"] = data["date"].min()
    result["end_date"] = data["date"].max()
    result["n_messages"] = len(data)
    result["n_authors"] = data["author"].nunique()
    result["n_medias"] = len(data[data["message"] == media_message])
    return result


def get_date_range(data):
    """
    Start date and end date of the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    _min, _max: str
        Start/end date
    """
    _min = data["date"].min().strftime('%d/%m/%Y')
    _max = data["date"].max().strftime('%d/%m/%Y')
    return _min, _max


def get_questions_by_name(data):
    """
    Number of questions for each participant in the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    n_questions: dict
        Name as key and number of questions as value
    """
    n_questions = {author: 0 for author in data["author"].unique()}

    for _, row in data.iterrows():
        is_question = ("?" in row["message"]) * 1
        n_questions[row["author"]] += is_question

    n_questions = {k: v for k, v in sorted(
        n_questions.items(), key=lambda item: item[1], reverse=True)}
    return n_questions


def get_number_of_message(data):
    """
    Total number of messages for each participant in the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    res: dict
        Name as key and number of messages as value
    """
    res = data.groupby("author").agg("count")["message"].to_dict()
    res = {k: v for k, v in sorted(
        res.items(), key=lambda item: item[1], reverse=True)}
    return res


def get_maximal_silence_period(data):
    """
    Maximal number of days without sending a message for each participant

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    res: dict
        Name as key, period of silence as value
    """
    def get_max(x): return max(
        (x['date']-x['date'].shift()).fillna(pd.Timedelta(seconds=0)))
    res = data.groupby("author").apply(get_max).to_dict()
    res = {k: str(v) for k, v in sorted(
        res.items(), key=lambda item: item[1], reverse=True)}
    return res


def get_mean_message_len(data):
    """
    Mean of the messages size for each participant in the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    res: dict
        Name as key, average message length as value
    """
    res = data.groupby("author").apply(lambda x: np.mean(
        [len(msg) for msg in x["message"]])).to_dict()
    res = {k: v for k, v in sorted(
        res.items(), key=lambda item: item[1], reverse=True)}
    return res


def percentage_msg_with_emoji(data):
    """
   Percentage of messages with one or more emoji for each participant in the conversation

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    res: dict
        Name as key, proportion of message with emoji as value
    """
    res = data.groupby("author").apply(lambda x: np.mean(
        [emoji_count(msg) != 0 for msg in x["message"]])).to_dict()
    res = {k: v for k, v in sorted(
        res.items(), key=lambda item: item[1], reverse=True)}
    return res


def get_nb_message_per_day(data):
    """
    Number of messages for each day

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    tmp: pd.DataFrame
        Count the number of message for each day in the conversation
    """
    days = pd.DataFrame([datetime.strptime(x, '%d/%m/%Y') for x in data["date"].dt.strftime('%d/%m/%Y')],
                        columns=["day"])

    tmp = pd.concat((data["date"], days), axis=1)
    tmp = tmp.groupby("day").agg("count").reset_index()
    return tmp


def get_moving_average_nb_message(data):
    """
    Moving number of message for a period of 7 days

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    tmp: pd.DataFrame
        Number of messages for a period of one week by rolling the date range
    """
    tmp = get_nb_message_per_day(data)

    # Add day not present in database
    _tmp = []

    for day in pd.date_range(tmp["day"].min(), tmp["day"].max(), freq='D'):
        if day not in tmp["day"]:
            to_append = pd.DataFrame([[day, 0]],
                                     columns=["day", "date"])
            _tmp.append(to_append)

    tmp = pd.concat((tmp, pd.concat(_tmp)), axis=0)

    # Sum of number of messages during 7 days (rolling)
    tmp = tmp.set_index('day').sort_index().rolling("7D").sum()
    tmp = tmp.reset_index()

    return tmp


def get_emoji_counter(data):
    """
    Count the emoji and distinguish between each participants

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    tmp: pd.DataFrame
        For each participant, emoji used and the associated number of utilisation
    """
    tmp = []

    for _, row in data.iterrows():
        emojis = [s for s in row["message"] if emoji_count(s) == 1]
        if len(emojis) != 0:
            for emoji in emojis:
                tmp.append((row["author"], emoji))

    tmp = pd.Series(tmp).value_counts().reset_index()
    tmp.columns = ["id", "count"]
    tmp["author"] = [x[0] for x in tmp["id"]]
    tmp["emoji"] = [x[1] for x in tmp["id"]]
    tmp = tmp.drop(columns=["id"])

    return tmp


def get_hourly_data(data):
    """
    For each hour and each participant, compute the number of message.
    Then normalize for each participant to have hourly distribution

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    data_copy: pd.DataFrame
        Normalized message frequency by hour for each participant
    """
    # Add hour for each row and count nb of messages for tuple author/hour
    data_copy = data.copy()
    data_copy["hour"] = data.apply(lambda x: x["date"].hour, axis=1)
    data_copy = data_copy[["author", "hour"]]
    data_copy = data_copy.groupby(["author", "hour"]).size().reset_index()
    data_copy.columns = ["author", "hour", "count"]
    data_copy = data_copy.pivot_table(
        index=["hour"], columns=["author"]).replace(np.nan, 0)
    data_copy = data_copy.T

    # Add hours not present
    for hour in range(24):
        if hour not in data_copy.columns:
            data_copy[hour] = 0

    # To int & sort columns
    data_copy = data_copy.astype(int)
    data_copy = data_copy.reindex(
        list(range(6, -1, -1)) + list(range(23, 6, -1)), axis=1)

    # Normalize
    data_copy = (data_copy.div(data_copy.sum(axis=1), axis=0) * 100).round(2)
    return data_copy


def get_daily_data(data):
    """
    For each day and each participant, compute the number of message.
    Then normalize for each participant to have daily distribution

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    data_copy: pd.DataFrame
        Normalized message frequency by day for each participant
    """
    # Add day for each row and count nb of messages for tuple author/hour
    data_copy = data.copy()
    data_copy["day"] = data.apply(lambda x: x["date"].strftime("%A"), axis=1)
    data_copy = data_copy[["author", "day"]]
    data_copy = data_copy.groupby(["author", "day"]).size().reset_index()
    data_copy.columns = ["author", "day", "count"]
    data_copy = data_copy.pivot_table(
        index=["day"], columns=["author"]).replace(np.nan, 0)
    data_copy = data_copy.T

    # Add days not present
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day not in data_copy.columns:
            data_copy[day] = 0

    # To int & Normalize
    data_copy = data_copy.astype(int)
    data_copy = (data_copy.div(data_copy.sum(axis=1), axis=0) * 100).round(2)

    return data_copy


def get_monthly_data(data):
    """
    For each month and each participant, compute the number of message.
    Then normalize for each participant to have monthly distribution

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe

    Returns
    -------
    data_copy: pd.DataFrame
        Normalized message frequency by month for each participant
    """
    # Add day for each row and count nb of messages for tuple author/hour
    data_copy = data.copy()
    data_copy["month"] = data.apply(lambda x: x["date"].strftime("%B"), axis=1)
    data_copy = data_copy[["author", "month"]]
    data_copy = data_copy.groupby(["author", "month"]).size().reset_index()
    data_copy.columns = ["author", "month", "count"]
    data_copy = data_copy.pivot_table(index=["month"], columns=[
                                      "author"]).replace(np.nan, 0)
    data_copy = data_copy.T

    # Add days not present
    for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
        if month not in data_copy.columns:
            data_copy[month] = 0

    # To int & Normalize
    data_copy = data_copy.astype(int)
    data_copy = (data_copy.div(data_copy.sum(axis=1), axis=0) * 100).round(2)

    return data_copy


def get_mean_media_interval(data, media_message):
    """
    For each participant, compute the average time between sending a media

    Parameters
    ----------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    media_message: str
        Message value when a media is omitted (language dependant)

    Returns
    -------
    res: dict
        Name as key and mean media interval as value
    """
    res = {}

    for author in data["author"].unique():
        # Get media data
        data_tmp = data[data["author"] == author]
        data_tmp_media = data_tmp[data_tmp["message"] == media_message]

        # Add first and last message
        data_tmp_media = pd.concat(
            (data.iloc[[0]], data_tmp_media), axis=0, ignore_index=True)
        data_tmp_media = pd.concat(
            (data_tmp_media, data.iloc[[-1]]), axis=0, ignore_index=True)

        # Get time interval between each media message
        intervals = (data_tmp_media["date"] -
                     data_tmp_media["date"].shift()).iloc[1:]
        # remove media too close (on peut en envoyer plusieurs à la fois avec peu de différence de temps entre deux)
        intervals = [t for t in intervals if t > timedelta(minutes=30)]
        mean_media_interval = np.mean(intervals)

        res[author] = mean_media_interval

    res = {k: ":".join(str(v.round("H")).split(":")[:-1])
           for k, v in sorted(res.items(), key=lambda item: item[1])}
    return res
