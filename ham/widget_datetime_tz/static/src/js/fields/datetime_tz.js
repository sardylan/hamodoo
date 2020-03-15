odoo.define('widget_datetime_tz.basic_fields', function (require) {
    "use strict";

    const registry = require('web.field_registry');
    const fields = require('web.basic_fields');

    const FieldDateTimeTZ = fields.FieldDateTime.extend({
        supportedFieldTypes: ['datetime'],

        init: function () {
            this._super.apply(this, arguments);
            this.formatOptions.timezone = false;
            if (this.value) {
                let offset = this._getTimezoneOffset();
                this.datepickerOptions.defaultDate = this.value.clone().add(offset, 'minutes');
            }
        },

        _getValue: function () {
            let value = this.datewidget.getValue();
            let offset = -this._getTimezoneOffset();
            return value && value.add(offset, 'minutes');
        },

        _renderEdit: function () {
            let offset = this._getTimezoneOffset();
            let value = this.value && this.value.clone().add(offset, 'minutes');
            this.datewidget.setValue(value);
            this.$input = this.datewidget.$input;
        },

        _getTimezoneOffset: function () {
            // return this.getSession().getTZOffset(this.value);
            return 0;
        }
    });

    registry.add('datetime_tz', FieldDateTimeTZ);

    return {
        FieldDateTimeTZ: FieldDateTimeTZ
    };
});
