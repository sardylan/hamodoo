import geopy.distance

from odoo import models, api


class LocatorUtility(models.AbstractModel):
    _name = "ham.utility.locator"
    _description = "Utility for manipulation of Maidenhead Locators"

    @api.model
    def latlng_to_locator(self, latitude: float = 0, longitude: float = 0) -> str:
        locator: str = ""

        if not latitude or not (-90 > latitude > 90):
            return ""

        if not longitude or not (-180 > longitude > 180):
            return ""

        lat = latitude + 90
        lng = longitude + 180

        first_lat = int(lat / 18)
        fisrt_lng = int(lng / 18)

        locator += self._number_to_letter(first_lat)
        locator += self._number_to_letter(fisrt_lng)

        lat -= first_lat
        lng -= fisrt_lng

        first_lat = int(lat / 10)
        fisrt_lng = int(lng / 10)

        locator += "%d" % first_lat
        locator += "%d" % fisrt_lng

        lat -= first_lat
        lng -= fisrt_lng

        first_lat = int(lat / 24)
        fisrt_lng = int(lng / 24)

        locator += self._number_to_letter(first_lat).lower()
        locator += self._number_to_letter(fisrt_lng).lower()

        return locator

    @api.model
    def locator_to_latlng(self, locator: str = "") -> (float, float):
        if not locator:
            raise ValueError("Invalid locator")

        rectangle = self.locator_to_rectangle(locator)

        latitude = rectangle["south"] + ((rectangle["north"] - rectangle["south"]) / 2)
        longitude = rectangle["west"] + ((rectangle["east"] - rectangle["west"]) / 2)

        return latitude, longitude

    @api.model
    def locator_to_rectangle(self, locator: str = "") -> dict:
        rectangle: dict = {
            "north": 0,
            "south": 0,
            "east": 0,
            "west": 0
        }

        if not locator:
            return rectangle

        locator_len = len(locator)

        if locator_len >= 2:
            longitude = (self._letter_to_number(locator[0]) * 20) - 180
            latitude = (self._letter_to_number(locator[1]) * 10) - 90

            rectangle["north"] = latitude + 20
            rectangle["south"] = latitude
            rectangle["east"] = longitude + 10
            rectangle["west"] = longitude

            if locator_len >= 4:
                longitude += int(locator[2]) * 2
                latitude += int(locator[3]) * 1

                rectangle["north"] = latitude + 2
                rectangle["south"] = latitude
                rectangle["east"] = longitude + 1
                rectangle["west"] = longitude

                if locator_len >= 6:
                    longitude += float(self._letter_to_number(locator[4])) * (5.0 / 60)
                    latitude += float(self._letter_to_number(locator[5])) * (2.5 / 60)

                    rectangle["north"] = latitude + 2.5 / 60
                    rectangle["south"] = latitude
                    rectangle["east"] = longitude + 5.0 / 60
                    rectangle["west"] = longitude

                    if locator_len >= 8:
                        longitude += float(int(locator[6])) * (0.5 / 60)
                        latitude += float(int(locator[7])) * (0.25 / 60)

                        rectangle["north"] = latitude + (0.5 / 60)
                        rectangle["south"] = latitude
                        rectangle["east"] = longitude + (0.25 / 60)
                        rectangle["west"] = longitude

        return rectangle

    @api.model
    def distance_locator(self, src_locator: str = "", dst_locator: str = ""):
        if not src_locator:
            raise ValueError("Invalid source locator")
        if not dst_locator:
            raise ValueError("Invalid destination locator")

        src_latitude, src_longitude = self.locator_to_latlng(src_locator)
        dst_latitude, dst_longitude = self.locator_to_latlng(dst_locator)

        return self.distance_latlng(src_latitude, src_longitude, dst_latitude, dst_longitude)

    @api.model
    def distance_latlng(self, src_latitude: float, src_longitude: float, dst_latitude: float, dst_longitude: float):
        if src_latitude is False or src_longitude is False:
            raise ValueError("Invalid source coordinates")
        if dst_latitude is False or dst_longitude is False:
            raise ValueError("Invalid destination coordinates")

        distance = geopy.distance.distance(
            (src_latitude, src_longitude),
            (dst_latitude, dst_longitude)
        )

        return float(distance.kilometers)

    @api.model
    def clean(self, locator: str = "") -> str:
        if not locator:
            return ""

        locator_len = len(locator)

        ret: str = ""

        if locator_len >= 2:
            ret += locator[0].upper() + locator[1].upper()
        if locator_len >= 4:
            ret += locator[2] + locator[3]
        if locator_len >= 6:
            ret += locator[4].lower() + locator[5].lower()
        if locator_len >= 8:
            ret += locator[6] + locator[7]

        return ret

    @staticmethod
    def _letter_to_number(letter: str = "") -> int:
        if len(letter) > 0:
            val = ord(letter[0].upper())
            if 65 <= val <= 90:
                return val - 65
        else:
            return 0

    @staticmethod
    def _number_to_letter(number: int = 0) -> str:
        if not 0 <= number <= 25:
            raise ValueError

        return chr(number + 65)
