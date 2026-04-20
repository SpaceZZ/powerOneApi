"""
Configurator: reads all settings from config.ini.
"""
import configparser
import sys


class Configurator:
    """
    Holds the configuration loaded from config.ini.
    Raises a clear error if the file is missing or a required key is absent.
    """

    def __init__(self, path="config.ini"):
        config = configparser.ConfigParser()
        read_files = config.read(path)

        if not read_files:
            sys.exit(
                f"ERROR: Configuration file '{path}' not found. "
                "Copy config.ini.example and fill in your credentials."
            )

        try:
            self.user = config["SETTINGS"]["user"]
            self.password = config["SETTINGS"]["password"]
            self.installationID = config["SETTINGS"]["installationID"]
            self.timezone = config["SETTINGS"]["timezone"]
            self.api_key = config["SETTINGS"]["api_key"]

            self.email = config["CREDENTIALS"]["email"]
            self.email_password = config["CREDENTIALS"]["password"]
            self.recipients = config["CREDENTIALS"]["recipients"]

            # Database — optional section; sql_handling will skip if absent
            if "DATABASE" in config:
                self.db_host = config["DATABASE"].get("host", "localhost")
                self.db_user = config["DATABASE"]["user"]
                self.db_password = config["DATABASE"]["password"]
                self.db_name = config["DATABASE"]["database"]
            else:
                self.db_host = None
                self.db_user = None
                self.db_password = None
                self.db_name = None

        except KeyError as e:
            sys.exit(f"ERROR: Missing required config key: {e}. Check your config.ini.")
