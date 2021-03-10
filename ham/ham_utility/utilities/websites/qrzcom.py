import logging

from odoo import models, api
from odoo.addons.ham_utility.libs.qrzcom_client import QRZComClient
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

QRZCOM_API_URL = "https://xmldata.qrz.com/xml/1.34/"
QRZCOM_API_APP_NAME = "ham.thehellnet.org 14.0"

_logger = logging.getLogger(__name__)


class QRZComUtility(models.AbstractModel):
    _name = "ham.utility.websites.qrzcom"
    _description = "Integration with QRZ.com API"

    @api.model
    def verify_credentials(self, username: str, password: str):
        if not username or not password:
            raise ValidationError(_("Invalid username or password"))

        try:
            qrz_com_client = QRZComClient(
                username=username,
                password=password
            )

            qrz_com_client.login()
        except ValueError as e:
            _logger.error(e)
            raise ValidationError(_("Unable to login"))

    @api.model
    def upload_qso(self, qso, callsign: str = "", code: str = ""):
        if not callsign or not code:
            _logger.error("Invalid login data. Username: %s - Code: %s" % (
                callsign, code
            ))
            raise ValidationError(_("Invalid login data"))

        if not qso:
            _logger.error("Invalid QSO")
            raise ValidationError(_("Invalid QSO"))

        # adif_utility = self.env["ham.utility.adif"]
        #
        # url = HRDLOG_API_UPLOAD_QSO
        #
        # adif_data = adif_utility.generate_adif_qso(qso)
        #
        # data = {
        #     "Callsign": callsign,
        #     "Code": code,
        #     "App": HRDLOG_API_APP_NAME,
        #     "ADIFData": adif_data
        # }
        #
        # response = requests.post(url=url, data=data)
        #
        # if response.status_code != 200:
        #     _logger.error("Unable to upload QSO to HRDLog. Status code %d: %s" % (
        #         response.status_code, response.content
        #     ))
        #     _logger.error("Data: %s" % data)
        #     raise ValidationError(_("Unable to upload QSO to HRDLog"))
        #
        # if b"error" in response.content.lower():
        #     _logger.error("Error publishing QSO: %s" % response.content)
        #     _logger.error("Data: %s" % data)
        #     raise ValidationError(_("Error publishing QSO"))

    @api.model
    def get_infos(self, callsigns: list):
        username = self.env.user.qrzcom_username
        password = self.env.user.qrzcom_password

        qrz_com_client = QRZComClient(
            username=username,
            password=password
        )

        qrz_com_client.login()
        _logger.info("Logged in in QRZ.com")

        result = {}

        for callsign in callsigns:
            _logger.info(f"Quering for {callsign}")
            result[callsign] = qrz_com_client.search(callsign)

        return result
