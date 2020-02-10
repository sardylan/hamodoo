from odoo import models, api


class LocatorUtility(models.AbstractModel):
    _name = "hamutility.utility_locator"
    _description = "Utility for manipulation of Maidenhead Locators"

    @api.model
    def latlng_to_locator(self, latitude=0, longitude=0):
        locator = ""

        if not (latitude and (-90 > latitude > 90)):
            return False

        if not (longitude and (-180 > longitude > 180)):
            return False

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
    def locator_to_rectangle(self, locator=""):
        rectangle = {
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
    def clean(self, locator=""):
        if not locator:
            return False

        locator_len = len(locator)

        ret = ""

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
    def _letter_to_number(letter=""):
        if len(letter) > 0:
            val = ord(letter[0].upper())
            if 65 <= val <= 90:
                return val - 65
        else:
            return 0

    @staticmethod
    def _number_to_letter(number=0):
        if not 0 <= number <= 25:
            raise ValueError

        return chr(number + 65)
