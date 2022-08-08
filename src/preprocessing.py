from datetime import datetime
import os
import re
import pandas as pd

from .utils import is_message

# =====> derive header from date_format ?!!
HEADER = r"(\d{2}/\d{2}/\d{4} à \d{2}:\d{2} - )"
DATE_FORMAT = '%d/%m/%Y à %H:%M'


def get_data_from_txt(f, header=HEADER, date_format=DATE_FORMAT):
    """doc"""
    tmp = []
    joined = " ".join(f)
    splitted = re.compile(header).split(joined)[1:]  # premier = vide
    msgs = [splitted[2 * i] + splitted[2 * i + 1] for i in range(len(splitted) // 2)]

    for msg in msgs:
        if is_message(msg):
            date_time_obj, author, message = preprocess_row(msg, date_format)
            to_append = pd.DataFrame([[date_time_obj, author, message]],
                                     columns=["date", "author", "message"])
            tmp.append(to_append)

    data = pd.concat(tmp, axis=0).reset_index(drop=True)
    return data


def preprocess_row(msg, date_format):
    """doc"""
    date, message = msg.split(" - ", 1)
    author, message = message.split(": ", 1)
    message = message[:-2]  # \n and space at the end
    date_time_obj = datetime.strptime(date, date_format)
    return date_time_obj, author, message


def read_data(data_path, file, header=HEADER, date_format=DATE_FORMAT):
    """doc"""
    _path = os.path.join(data_path, file)
    f = open(_path, "r")
    data = get_data_from_txt(f, header, date_format)
    return data



