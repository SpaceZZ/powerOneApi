"""
Main application entry point.
All code for the inverter api is located in the aurora_vision_api module
"""

import aurora_vision_api
import configurator

if __name__ == "__main__":
    #read configuration from the file
    config = configurator.Configurator()

    session = aurora_vision_api.Session(user=config.user, password=config.password,
                                        installationID=config.installationID, country=config.country)
    #result = session.get_data()
    #print(result)

    result = session.get_data(extended=True)
    print(result)
