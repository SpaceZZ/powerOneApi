"""
Main application entry point.
All code for the inverter api is located in the aurora_vision_api module
"""
import aurora_vision_api
import configurator
import email_sender
import html_render
import pv_calculator
import image_charts

if __name__ == "__main__":
    #read configuration from the file
    config = configurator.Configurator()

    session = aurora_vision_api.Session(user=config.user, password=config.password,
                                        installationID=config.installationID, country=config.country)
    result = session.get_data()
    result_extended = session.get_data(extended=True)
    # if there was a success in the getting the values
    if result:
        if result_extended:
            data = {key: value for key, value in result_extended.items() if key != "today"}
            # get maximum power
            max_time, max_power = pv_calculator.calculate_max_power(data)
            non_zero_data, start_time, end_time, mid_time = pv_calculator.get_only_valid_data(data)
            chart_link = image_charts.create_link(non_zero_data.values(), start_time, end_time, mid_time)
        else:
            max_time = ""
            max_power = 0
            chart_link = ""
        html = html_render.render(result, max_time, max_power, chart_link)
        sender = email_sender.EmailSender(email=config.email, password=config.email_password, recipients=config.recipients)
        sender.send(html)
