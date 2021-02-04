import calendar
import datetime

from odoo import models, api


class DtUtility(models.AbstractModel):
    _name = "ham.utility.dt"
    _description = "Datetime utilities"

    @api.model
    def compute_start_end(self, mode: str = "", now: datetime.datetime = datetime.datetime.utcnow()) -> tuple:
        if not mode:
            raise ValueError("No mode")

        dt_start: datetime.datetime
        dt_end: datetime.datetime

        if mode == "last_day":
            dt_offset = now - datetime.timedelta(days=1)
            dt_start = dt_offset.replace(hour=0, minute=0, second=0, microsecond=0)
            dt_end = dt_start.replace(hour=23, minute=59, second=59)
        elif mode == "last_week":
            dt_offset = now - datetime.timedelta(weeks=1)
            dt_temp = dt_offset.replace(hour=0, minute=0, second=0, microsecond=0)
            dt_start = dt_temp - datetime.timedelta(days=dt_temp.weekday())
            dt_end = dt_start + datetime.timedelta(days=6)
        elif mode == "last_month":
            days = calendar.monthrange(now.year, now.month)[1]
            dt_offset = now - datetime.timedelta(days=days)
            dt_start = dt_offset.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            day = calendar.monthrange(dt_start.year, dt_start.month)[1]
            dt_end = dt_start.replace(day=day, hour=23, minute=59, second=59)
        elif mode == "last_year":
            dt_offset = now - datetime.timedelta(days=365)
            dt_start = dt_offset.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            dt_end = dt_start.replace(month=12, day=31, hour=23, minute=59, second=59)
        else:
            raise NotImplementedError

        return dt_start, dt_end
