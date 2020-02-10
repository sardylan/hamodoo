#!/bin/bash

git submodule init
git submodule update

if [[ ! -d venv ]]; then
    python3 -m venv venv
fi

./venv/bin/pip3 \
    install \
    --no-binary :all: \
    --only-binary poetry,tomlkit,pastel,pygount \
    --requirement ./odoo/requirements.txt \
    --requirement ./web/requirements.txt \
    --requirement ./requirements.txt
