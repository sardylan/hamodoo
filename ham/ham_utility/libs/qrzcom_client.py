import requests
from lxml import etree


class QRZComClient:
    def __init__(self, username: str, password: str):
        self._username: str = username
        self._password: str = password

        self._token: str = ""

    def login(self):
        url = self._compute_url()

        data = {
            "username": self._username,
            "password": self._password
        }

        response = requests.post(url=url, data=data)

        response_body = etree.fromstring(response.content)
        keys = response_body.xpath("//qrz:Key", namespaces={"qrz": "http://xmldata.qrz.com"})
        if len(keys) != 1:
            raise ValueError("Unable to login")

        self._token = keys[0].text

    def search(self, callsign: str = "") -> dict:
        if not callsign:
            raise ValueError("Empty Callsigin")

        url = self._compute_url()

        data = {
            "s": self._token,
            "callsign": callsign
        }

        response = requests.post(url=url, data=data)

        response_body = etree.fromstring(response.content)
        xml_error = response_body.xpath("//qrz:Error", namespaces={"qrz": "http://xmldata.qrz.com"})
        if len(xml_error) > 0:
            message = xml_error[0].text
            raise ValueError(f"Unable to find {callsign}: {message}")

        xml_callsign = response_body.xpath("//qrz:Callsign", namespaces={"qrz": "http://xmldata.qrz.com"})
        if len(xml_callsign) != 1:
            raise ValueError(f"Unable to retrieve informations for {callsign}")

        values = {}

        items = xml_callsign[0]
        for item in items:
            key = item.tag.split("}")[1]
            value = item.text

            values[key] = value

        return values

    @staticmethod
    def _compute_url(api_version: str = "1.34") -> str:
        return f"https://xmldata.qrz.com/xml/{api_version}/"
