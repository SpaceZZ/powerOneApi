"""
Configurator for the options to the script
"""
import configparser


class Configurator:
    """
    Holds the configuration loaded from the file+
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.user = config['SETTINGS']['user']
        self.password = config['SETTINGS']['password']
        self.installationID = config['SETTINGS']['installationID']
        self.country = config['SETTINGS']['country']
        self.email = config['CREDENTIALS']['email']
        self.email_password = config['CREDENTIALS']['password']
        self.recipients = config['CREDENTIALS']['recipients']
