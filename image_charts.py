def create_link(non_zero_data, start_time, end_time, mid_time):
    """
    Builds an image-charts.com URL for a styled line chart of power production.
    :param non_zero_data: iterable of numeric watt values
    :param start_time: HH:MM:SS string for the x-axis left label
    :param end_time:   HH:MM:SS string for the x-axis right label
    :param mid_time:   HH:MM:SS string for the x-axis middle label
    :return: URL string
    :rtype: str
    """
    values = ",".join(str(item) for item in non_zero_data)
    # Chart parameters:
    #   cht=lc         line chart
    #   chs=990x280    wider and taller
    #   chd=a:<data>   auto-scaled data
    #   chco=F39C12    orange line
    #   chf=bg,s,1a1a2e  dark background
    #   chm=B,...      filled area under curve (amber fill)
    #   chxt=x,y       show both axes
    #   chxl=0:|...    x-axis labels
    #   chg=25,20      grid lines (25% x-spacing, 20% y-spacing)
    #   chls=3         line thickness 3px
    #   chma=30,20,20,30  margins (left,right,top,bottom)
    link = (
        "https://image-charts.com/chart"
        "?cht=lc"
        "&chs=990x280"
        "&chd=a:<data>"
        "&chco=F39C12"
        "&chf=bg,s,1a1a2e"
        "&chm=B,2C2C54,0,0,0"
        "&chxt=x,y"
        "&chxs=0,AAAAAA,13|1,AAAAAA,13"
        "&chxl=0:|<start>|<mid>|<finish>"
        "&chg=25,20,2,2,FFFFFF15"
        "&chls=3"
        "&chma=30,20,20,30"
    )
    link = link.replace("<data>", values)
    link = link.replace("<start>", start_time)
    link = link.replace("<finish>", end_time)
    link = link.replace("<mid>", mid_time)
    return link
