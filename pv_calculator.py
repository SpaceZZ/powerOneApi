from datetime import datetime


def calculate_max_power(data):
    """
    Function calculates the maximum
    :param data:
    :type data:
    :return:
    :rtype:
    """
    new_data = {key: float(value["value"]) for key, value in data.items()}
    if new_data:
        max_power = max(new_data, key=new_data.get)
    else:
        return 0, ""
    return max_power, new_data[max_power]


def findMiddle(input_list):
    middle = float(len(input_list)) / 2
    if middle % 2 != 0:
        return input_list[int(middle - 0.5)]
    else:
        return input_list[int(middle)]


def get_only_valid_data(data):
    """
    Get only non zero or null data into the dictionary
    :param data:
    :type data:
    :return:
    :rtype:
    """
    new_data = {key: float(value["value"]) for key, value in data.items()}
    non_zero_data = {
        key.split(" ")[1]: round(value) for key, value in new_data.items() if value != 0
    }
    start_time = list(non_zero_data.keys())[0]
    end_time = list(non_zero_data.keys())[-1]
    mid_time = findMiddle(list(non_zero_data.keys()))

    return non_zero_data, start_time, end_time, mid_time


def get_start_time(data):
    return None


def get_end_time(data):
    return None
