import numpy as np
from emoji import emoji_count
import pandas as pd
from datetime import datetime, timedelta


def get_basic_infos(data, media_message):
    """doc"""
    result = {}
    result["start_date"] = data["date"].min()
    result["end_date"] = data["date"].max()
    result["n_messages"] = len(data)
    result["n_authors"] = data["author"].nunique()
    result["n_medias"] = len(data[data["message"] == media_message])
    return result


def get_date_range(data):
    """doc"""
    _min = data["date"].min().strftime('%d/%m/%Y')
    _max = data["date"].max().strftime('%d/%m/%Y')
    return _min, _max


def get_questions_by_name(data):
    """doc"""
    n_questions = {author: 0 for author in data["author"].unique()}

    for _, row in data.iterrows():
        is_question = ("?" in row["message"]) * 1
        n_questions[row["author"]] += is_question

    n_questions = {k: v for k, v in sorted(n_questions.items(), key=lambda item: item[1], reverse=True)}
    return n_questions


def get_number_of_message(data):
    """number total de message par personne"""
    res = data.groupby("author").agg("count")["message"].to_dict()
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    return res


def get_maximal_silence_period(data):
    """doc"""
    get_max = lambda x: max((x['date']-x['date'].shift()).fillna(pd.Timedelta(seconds=0)))
    res = data.groupby("author").apply(get_max).to_dict()
    res = {k: str(v) for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    return res


def get_mean_message_len(data):
    """taille moyenne des messages par personne"""
    res = data.groupby("author").apply(lambda x: np.mean([len(msg) for msg in x["message"]])).to_dict()
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    return res


def percentage_msg_with_emoji(data):
    """percentage of message containing one or more emoji"""
    res = data.groupby("author").apply(lambda x: np.mean([emoji_count(msg) != 0 for msg in x["message"]])).to_dict()
    res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True)}
    return res


def get_nb_message_per_day(data):
    """doc"""
    days = pd.DataFrame([datetime.strptime(x, '%d/%m/%Y') for x in data["date"].dt.strftime('%d/%m/%Y')],
                    columns=["day"])

    tmp = pd.concat((data["date"], days), axis=1)
    tmp = tmp.groupby("day").agg("count").reset_index()
    return tmp


def get_moving_average_nb_message(data):
    """doc"""
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
    """doc"""
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
    """doc"""
    # Add hour for each row and count nb of messages for tuple author/hour
    data_copy = data.copy()
    data_copy["hour"] = data.apply(lambda x: x["date"].hour, axis=1)
    data_copy = data_copy[["author", "hour"]]
    data_copy = data_copy.groupby(["author", "hour"]).size().reset_index()
    data_copy.columns = ["author", "hour", "count"]
    data_copy = data_copy.pivot_table(index=["hour"], columns=["author"]).replace(np.nan, 0)
    data_copy = data_copy.T

    # Add hours not present
    for hour in range(24):
        if hour not in data_copy.columns:
            data_copy[hour] = 0

    # To int & sort columns
    data_copy = data_copy.astype(int)
    data_copy = data_copy.reindex(list(range(6, -1, -1)) + list(range(23, 6, -1)), axis=1)

    # Normalize
    data_copy = (data_copy.div(data_copy.sum(axis=1), axis=0) * 100).round(2)
    return data_copy


def get_daily_data(data):
    """doc"""
    # Add day for each row and count nb of messages for tuple author/hour
    data_copy = data.copy()
    data_copy["day"] = data.apply(lambda x: x["date"].strftime("%A"), axis=1)
    data_copy = data_copy[["author", "day"]]
    data_copy = data_copy.groupby(["author", "day"]).size().reset_index()
    data_copy.columns = ["author", "day", "count"]
    data_copy = data_copy.pivot_table(index=["day"], columns=["author"]).replace(np.nan, 0)
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
    """doc"""
    # Add day for each row and count nb of messages for tuple author/hour
    data_copy = data.copy()
    data_copy["month"] = data.apply(lambda x: x["date"].strftime("%B"), axis=1)
    data_copy = data_copy[["author", "month"]]
    data_copy = data_copy.groupby(["author", "month"]).size().reset_index()
    data_copy.columns = ["author", "month", "count"]
    data_copy = data_copy.pivot_table(index=["month"], columns=["author"]).replace(np.nan, 0)
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
    """doc"""
    res = {}

    for author in data["author"].unique():
        # Get media data
        data_tmp = data[data["author"] == author]
        data_tmp_media = data_tmp[data_tmp["message"] == media_message]

        # Add first and last message
        data_tmp_media = pd.concat((data.iloc[[0]], data_tmp_media), axis=0, ignore_index=True)
        data_tmp_media = pd.concat((data_tmp_media, data.iloc[[-1]]), axis=0, ignore_index=True)

        # Get time interval between each media message
        intervals = (data_tmp_media["date"] - data_tmp_media["date"].shift()).iloc[1:]
        # remove media too close (on peut en envoyer plusieurs à la fois avec peu de différence de temps entre deux)
        intervals = [t for t in intervals if t > timedelta(minutes=30)]
        mean_media_interval = np.mean(intervals)

        res[author] = mean_media_interval

    #res = {k: str(v) for k, v in sorted(res.items(), key=lambda item: item[1])}
    res = {k: ":".join(str(v.round("H")).split(":")[:-1])
           for k, v in sorted(res.items(), key=lambda item: item[1])}
    return res
