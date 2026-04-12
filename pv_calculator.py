import logging

logger = logging.getLogger(__name__)


def calculate_max_power(data):
    """
    Function calculates the time and wattage of peak power production.
    :param data: dict of {timestamp: {"value": float, "unit": str}}
    :return: (peak_time, peak_watts) or ("", 0) if data is empty
    :rtype: tuple
    """
    # Build a plain float dict keyed by timestamp
    float_data = {key: float(value["value"]) for key, value in data.items()}
    if not float_data:
        return "", 0

    # max() on the dict returns the key whose value is highest
    peak_time = max(float_data, key=float_data.get)
    peak_watts = float_data[peak_time]
    return peak_time, peak_watts


def find_middle(input_list):
    """
    Function finds the middle item from the list.
    :param input_list: list
    :return: middle element
    """
    middle = float(len(input_list)) / 2
    if middle % 2 != 0:
        return input_list[int(middle - 0.5)]
    else:
        return input_list[int(middle)]


def get_only_valid_data(data):
    """
    Get only non-zero / non-null data points.
    Returns empty values gracefully when there is no production (night, cloudy day).
    :param data: dict of {timestamp: {"value": float|None, "unit": str}}
    :return: (non_zero_data, start_time, end_time, mid_time)
    :rtype: tuple
    """
    float_data = {key: float(value["value"]) for key, value in data.items() if value["value"] is not None}
    non_zero_data = {
        key.split(" ")[1]: round(value)
        for key, value in float_data.items()
        if value != 0
    }

    if not non_zero_data:
        logger.warning("No non-zero production data found (night or cloudy day?)")
        return {}, "", "", ""

    keys = list(non_zero_data.keys())
    start_time = keys[0]
    end_time = keys[-1]
    mid_time = find_middle(keys)

    return non_zero_data, start_time, end_time, mid_time
