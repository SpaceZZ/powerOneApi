import datetime
import time
import requests
import json


class Session:
    """
    Class session holds all the information related to the Aurora vision api
    """

    _link = (
        r"https://easyview.auroravision.net/easyview/services/gmi/summary/PlantEnergy.json?eids=<installationID>&tz=<timezone>"
        r"&nDays=<days>&now=true&dateLabel=yyyy-MM-dd-+HH%3Amm%3Ass+zzz&locale=en&fields=GenerationEnergy&v=2.1.52"
    )
    _day_link = (
        r"https://easyview.auroravision.net/easyview/services/gmi/summary.json?eids=<installationID>&tz=<timezone>&start=<startDay>"
        r"&end=<endDay>&range=1D&fields=GenerationPower&binSize=Min15&bins=true&v=2.1.52&_=1578052570735 "
    )
    _headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,pl;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    }

    def __init__(self, user, password, installationID, country, headers=None):
        self._user = user
        self._password = password
        self._installationID = installationID
        self._country = country
        if headers:
            self._headers = headers
        else:
            self._headers = Session._headers

    def get_data(self, extended=False):
        """
        Method returns the power measurement from the installation
        :return: Today production
        :rtype:
        """
        if extended:
            api_link = self._construct_extended_api_link()
        else:
            api_link = self._construct_api_link()

        try:
            response = requests.get(
                api_link,
                auth=(self._user, self._password),
                headers=self._headers,
                timeout=15,
            )
            if response.status_code == 200:
                data = self._convert_response_to_json(response.content)
                return data
        except TimeoutError:
            print("Timeout error")
            return {}
        except Exception as ex:
            print(f"Following exception has occurred while executing the request {ex}")
            return {}

    def _construct_api_link(self):
        """
        Method constructs the link to be called through the object
        :return:
        :rtype:
        """
        link = self._link.replace("<installationID>", self._installationID)
        link = link.replace("<timezone>", self._country)
        link = link.replace("<days>", r"0%2C1%2C2")
        return link

    def _convert_response_to_json(self, content):
        """
        Method converts the received response from the
        :param content:
        :type content:
        :return: a dict of all labels returned from the response
        :rtype: dict
        """
        result = {}
        if content:
            try:
                data = json.loads(content)
                if data["status"] == "SUCCESS":
                    fields = data["fields"]
                    for field in fields:
                        # not extended json, regular data
                        if field["type"] != "bins":
                            # if {"type":"windowRequest","receiver":"legend","func":"Diff","id":"historical"} as label
                            if field["label"].startswith("{"):
                                result["today"] = self._generate_value_unit_dict(value=field["value"], raw_unit=field["units"])
                            else:
                                result[field["label"]] = self._generate_value_unit_dict(value=field["value"], raw_unit=field["units"])
                        else:
                            for bin_item in field["values"]:
                                _datetime = self._convert_epoch_to_string(
                                    bin_item["start"]
                                )
                                result[_datetime] = self._generate_value_unit_dict(bin_item["value"], "watts")
                    return result
            except ValueError:
                print("Didn't find the labels in the api response")
                return result
        else:
            print("Body of the response was empty")
            return result

    def _construct_extended_api_link(self):
        """
        Method to get extended data, by default it asks about today
        :return:
        :rtype:
        """
        d = datetime.date.today()
        d_end = d + datetime.timedelta(1)
        d = d.strftime("%Y%m%d")
        d_end = d_end.strftime("%Y%m%d")

        link = self._day_link.replace("<installationID>", self._installationID)
        link = link.replace("<timezone>", self._country)
        link = link.replace("<startDay>", d)
        link = link.replace("<endDay>", d_end)
        return link

    def _convert_epoch_to_string(self, epoch):
        """
        Method converts from epoch time to string representation
        :param param:
        :type param:
        :return:
        :rtype:
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

    def _generate_value_unit_dict(self, value, raw_unit):
        """
        Method creates value unit pair
        :param value:
        :type value:
        :param raw_unit:
        :type raw_unit:
        :return:
        :rtype:
        """
        units = {'kilowatts': 'kW',
                 'watts': 'W',
                 'kilowatt-hours': 'kWh',
                 'megawatt-hours': 'MWh'}
        return {'value': value, 'unit': units.get(raw_unit, '')}
