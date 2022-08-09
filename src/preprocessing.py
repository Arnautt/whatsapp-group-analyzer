import os
import re
from datetime import datetime

import pandas as pd

from .utils import is_message


def get_data_from_txt(f, header, date_format):
    """
    Get raw data from text conversation file

    Parameters
    ----------
    f: io.TextIOWrapper
        Opened conversation file
    header: str
        Regex of the date format + the sign separator between date and name,
        i.e. regex for the part before the names in the conversation
    date_format: str
        Datetime format of the conversation's date

    Returns
    -------
    data: pd.DataFrame
        Raw dataframe with all message in three columns: date, author and message
    """
    tmp = []
    joined = " ".join(f)
    splitted = re.compile(header).split(joined)[1:]  # premier = vide
    msgs = [splitted[2 * i] + splitted[2 * i + 1]
            for i in range(len(splitted) // 2)]

    for msg in msgs:
        if is_message(msg):
            date_time_obj, author, message = preprocess_row(msg, date_format)
            to_append = pd.DataFrame([[date_time_obj, author, message]],
                                     columns=["date", "author", "message"])
            tmp.append(to_append)

    data = pd.concat(tmp, axis=0).reset_index(drop=True)
    return data


def preprocess_row(msg, date_format):
    """
    Pre-process a single message

    Parameters
    ----------
    msg: str
        A single message with date, name and main message
    date_format: str
        Datetime format of the conversation's date

    Returns
    -------
    date_time_obj: datetime object
        Date of the message
    author: str
        Name of the message sender
    message: str
        Message send
    """
    date, message = msg.split(" - ", 1)
    author, message = message.split(": ", 1)
    message = message[:-2]  # \n and space at the end
    date_time_obj = datetime.strptime(date, date_format)
    return date_time_obj, author, message


def read_data(data_path, file, header, date_format):
    """
    Get WhatsApp conversation as a pandas DataFrame

    Parameters
    ----------
    data_path: str
        Path where all data are stored
    file: str
        Name of the conversation file
    header: str
        Regex of the date format + the sign separator between date and name,
        i.e. regex for the part before the names in the conversation
    date_format: str
        Datetime format of the conversation's date

    Returns
    -------
    data: pd.DataFrame
        Pre-processed conversation dataframe
    """
    _path = os.path.join(data_path, file)
    f = open(_path, "r")
    data = get_data_from_txt(f, header, date_format)
    return data
