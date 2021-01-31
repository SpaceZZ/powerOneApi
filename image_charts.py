import requests


def create_link(non_zero_data, start_time, end_time, mid_time):
    """
    Function creates the
    :param data:
    :type data:
    :return:
    :rtype:
    """
    non_zero_data = [str(item) for item in non_zero_data]
    values = ",".join(non_zero_data)
    link = r"https://image-charts.com/chart?cht=lc&chs=990x200&chd=a:<data>&chxt=x,y&chm=B,00FF00,0,0,0&&chxl=0:|<start>|<mid>|<finish>"
    link = link.replace("<data>", values)
    link = link.replace("<start>", start_time)
    link = link.replace("<finish>", end_time)
    link = link.replace("<mid>", mid_time)
    return link
