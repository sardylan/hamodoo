#!/bin/bash

set -x

cd /odoo || exit 1

if [ -z "${TEST_FLAGS}" ]; then
  ODOO_CMD_RUN="-i tournaments"
else
  ODOO_CMD_RUN="--limit-time-cpu=9999999 --limit-time-real=9999999 --stop-after-init ${TEST_FLAGS}"
fi

if [ -z "${DB_NAME}" ]; then
  ODOO_CMD_DATABASE=""
else
  ODOO_CMD_DATABASE="--database=\"${DB_NAME}\""
fi

if [ -z "${DATADIR}" ]; then
  ODOO_CMD_DATADIR="/data"
else
  ODOO_CMD_DATADIR="${DATADIR}"
fi

chown odoo:odoo "${ODOO_CMD_DATADIR}"

su \
  --preserve-environment \
  --shell /bin/bash \
  --command \
  "/venv/bin/python3 \
    /odoo/odoo-bin \
    --addons-path=\"/odoo/odoo/addons,/odoo/addons,/addons\" \
    --http-port=\"${HTTP_PORT:-8069}\" \
    --longpolling-port=\"${LONGPOLLING_PORT:-8072}\" \
    --data-dir=\"${ODOO_CMD_DATADIR}\" \
    --workers=\"${WORKERS:-2}\" \
    --db_host=\"${DB_HOST:-postgres}\" \
    --db_port=\"${DB_PORT:-5432}\" \
    --db_user=\"${DB_USERNAME:-odoo}\" \
    --db_password=\"${DB_PASSWORD:-odoo}\" \
    ${ODOO_CMD_DATABASE} \
    --proxy-mode \
    --load=\"web\" \
    ${ODOO_CMD_RUN}" \
  odoo

exit ${?}
