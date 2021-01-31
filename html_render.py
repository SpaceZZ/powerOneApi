import datetime

def render(data, max_time=None, max_power=None, image_link = ""):
    """
    Function renders the html to be returned
    :return:
    :rtype:
    """
    if image_link:
        image_link = f"<img src={image_link}/>"
    else:
        image_link = ""
    html = r"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
              border-collapse: collapse;
              width: 100%;
            }
            
            td, th {
              border: 1px solid #dddddd;
              text-align: left;
              padding: 8px;
            }
            </style>
            </head>
                       
            <p>Produkcja PV:</p>
            <table>
              <tr>
                <th>Okres</th>
                <th>Wartość</th>
                <th>Jednostka</th>
              </tr>
            """ + render_data(data) +\
           """
            </table>
            <br>
            """ + image_link + f"<p>Największa moc: {max_time} - {max_power:.1f} W</p>" + f"<p>Dane pobrane o {datetime.datetime.now()}</p>" + """
            </body>
            </html>
            """
    return html

def render_data(data):
    """
    Method render into thable the measurements
    :return:
    :rtype:
    """
    result = ""
    raw_html = r"""
             <tr>
                <td><label></td>
                <td><value></td>
                <td><unit></td>
            </tr>"""

    for key, value in data.items():
        html = raw_html.replace("<label>", key)
        html = html.replace("<value>", value['value'])
        html = html.replace("<unit>", value['unit'])
        result += html
    return result
