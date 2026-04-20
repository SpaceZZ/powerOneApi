def create_link(non_zero_data, start_time, end_time, mid_time, irradiance_values=None):
    """
    Builds an image-charts.com URL for a styled line chart of power production,
    with an optional second series for irradiance (W/m²).

    :param non_zero_data:      iterable of numeric watt values (AC power)
    :param start_time:         HH:MM:SS string for the x-axis left label
    :param end_time:           HH:MM:SS string for the x-axis right label
    :param mid_time:           HH:MM:SS string for the x-axis middle label
    :param irradiance_values:  optional list of W/m² integers aligned to non_zero_data
    :return: URL string
    :rtype: str
    """
    power_str = ",".join(str(item) for item in non_zero_data)

    if irradiance_values:
        irr_str = ",".join(str(v) for v in irradiance_values)
        # Two series: power (orange) + irradiance (sky blue)
        # chd=a: auto-scales both on the same Y axis — fine since both are ~0–1000+ range
        chd   = f"a:{power_str}|{irr_str}"
        chco  = "F39C12,5DADE2"       # orange, sky-blue
        chls  = "3|2"                  # power thicker, irradiance thinner
        chm   = "B,2C2C54,0,0,0"      # fill only under power (series 0)
        legend = "&chdl=Moc+AC+(W)|Nasłonecznienie+(W/m²)&chdlp=b&chdls=AAAAAA,11"
    else:
        chd   = f"a:{power_str}"
        chco  = "F39C12"
        chls  = "3"
        chm   = "B,2C2C54,0,0,0"
        legend = ""

    # Chart parameters:
    #   cht=lc           line chart
    #   chs=990x300      slightly taller to fit legend
    #   chd=a:...        auto-scaled data (one or two series)
    #   chco=...         line colour(s)
    #   chf=bg,s,1a1a2e  dark background
    #   chm=B,...        filled area under power curve
    #   chxt=x,y         show both axes
    #   chxl=0:|...      x-axis labels
    #   chg=25,20,...    grid lines
    #   chls=...         line thickness per series
    #   chma=...         margins (left,right,top,bottom)
    link = (
        "https://image-charts.com/chart"
        "?cht=lc"
        "&chs=990x300"
        f"&chd={chd}"
        f"&chco={chco}"
        "&chf=bg,s,1a1a2e"
        f"&chm={chm}"
        "&chxt=x,y"
        "&chxs=0,AAAAAA,13|1,AAAAAA,13"
        f"&chxl=0:|{start_time}|{mid_time}|{end_time}"
        "&chg=25,20,2,2,FFFFFF15"
        f"&chls={chls}"
        "&chma=30,20,20,30"
        + legend
    )
    return link
