#!/usr/bin/python3
#
# Prepare script for Odoo Installation
#
# Version changelog:
#
# 1. First implementation
#

import datetime
import glob
import json
import os
import subprocess
import sys

import pkg_resources
from colorama import Fore, Style

PREPARE_VERSION = 2

PREPARE_CONFIG_FILE = "__prepare__.json"

PIP_ONLY_BINARY = []
PIP_CONSTRAINT = []


def exit_error(error_code: int = -1, message: str = ""):
    print()
    print(Fore.LIGHTRED_EX + Style.BRIGHT + "ERROR!!!" + Style.RESET_ALL + Fore.RESET)
    print(Fore.LIGHTRED_EX + ("Exit code: %d" % error_code) + Fore.RESET)

    if message:
        print(Fore.LIGHTRED_EX + message + Fore.RESET)

    print()

    sys.exit(error_code)


def execute(args, skip_error: bool = False, cwd: str = ".", env: dict = None):
    if not args:
        return

    if env is None:
        env = {}

    if isinstance(args, list):
        cmd = " ".join(args)
    else:
        cmd = args

    print()
    print()
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    $ " + cmd + Style.RESET_ALL + Fore.RESET)
    print()

    extra = {}

    if cwd:
        extra["cwd"] = cwd

    if len(env) > 0:
        extra["env"] = env

    pr = subprocess.run(args=cmd, shell=True, **extra)
    cmd_result = pr.returncode

    print()

    if not skip_error and cmd_result != 0:
        exit_error(cmd_result)


def print_title(title: str = ""):
    print(Fore.LIGHTRED_EX + Style.BRIGHT + title + Style.RESET_ALL + Fore.RESET)
    print()


def print_completed(ts_duration):
    print()
    print(Fore.LIGHTRED_EX + "completed!!" + Fore.RESET)
    print()
    print("Duration: " + Fore.LIGHTBLUE_EX + str(ts_duration) + Fore.RESET)
    print()
    print()
    print()


def print_step(message: str = ""):
    if not message:
        return

    print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "    " + message + Style.RESET_ALL + Fore.RESET)
    print()


def env_prepend(key, value):
    items = []

    if key in os.environ:
        items.extend([x.strip() for x in os.environ[key].split(":") if x])

    items.insert(0, value)

    os.environ[key] = ":".join(items)


def parse_config():
    if not os.path.exists(PREPARE_CONFIG_FILE):
        return

    fd = open(PREPARE_CONFIG_FILE, "r")
    raw_content = fd.read()
    fd.close()

    config_data = json.loads(raw_content)

    if "python_dir" in config_data:
        python_dir = config_data["python_dir"]

        env_prepend("PATH", "%s/bin" % python_dir)

        print()
        print("Using python from \033[1;35m%s\033[0m" % python_dir)
        print()

    for item in config_data["only_binary"]:
        PIP_ONLY_BINARY.append(item)

    for item in config_data["constraint_files"]:
        PIP_CONSTRAINT.append(item)


def print_header():
    print()
    print("--------------------------------------")

    print(Fore.WHITE + Style.BRIGHT
          + "Prepare script version "
          + Style.RESET_ALL + Fore.RESET
          + Fore.LIGHTBLUE_EX + Style.BRIGHT
          + ("%d" % PREPARE_VERSION)
          + Style.RESET_ALL + Fore.RESET)

    print("--------------------------------------")
    print()


def git_configure():
    execute("git config --global credential.helper \"cache --timeout=300\"")


def git_align():
    execute("git submodule init")
    execute("git submodule update")


def venv_create():
    if os.path.isdir("venv"):
        return

    execute("python3 -m venv venv")


def venv_requirements():
    requirements_files = []

    reqs = {}

    for file_path in glob.iglob(pathname="**", recursive=True):
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)

        if file_name != "requirements.txt":
            continue

        if "openerp" in file_dir or "odoo" in file_dir:
            if os.path.basename(file_dir) == "doc":
                continue

        requirements_files.append(file_path)

    for requirements_file in requirements_files:
        print("Reading %s..." % requirements_file)
        fd = open(requirements_file, "r")
        file_content = fd.read()
        fd.close()

        rows = file_content.splitlines()
        parsed_reqs = pkg_resources.parse_requirements(rows)
        items = [x for x in parsed_reqs]

        for item in items:
            if item.marker and not item.marker.evaluate():
                continue

            if item.name not in reqs:
                reqs[item.name] = []

            reqs[item.name].extend(item.specs)

    for key, value in reqs.items():
        versions = [x[1] for x in value]
        versions.sort(key=lambda x: pkg_resources.parse_version(x), reverse=True)
        reqs[key] = versions and versions[0] or None

    reqs["Cython"] = None

    reqs = sorted(reqs.items(), key=lambda x: x[0])

    reqs_args = [value and "%s==%s" % (key, value) or key for key, value in reqs]
    if not reqs_args:
        return

    args = [
        "./venv/bin/pip3",
        "install",
        "--no-binary", ":all:",
    ]

    if PIP_ONLY_BINARY:
        args.extend(["--only-binary", ",".join(PIP_ONLY_BINARY)])

    for item in PIP_CONSTRAINT:
        args.extend(["--constraint", item])

    args.extend(reqs_args)

    execute(args)


def first_run_cmd_print():
    addons_dirs = [
        "odoo/odoo/addons",
        "odoo/addons"
    ]

    for file_path in glob.iglob(pathname="*/*/*", recursive=True):
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)

        if file_name != "__manifest__.py":
            continue

        module_dir = os.path.dirname(file_dir)
        if "test" in module_dir:
            continue

        if module_dir not in addons_dirs:
            addons_dirs.append(module_dir)

    addons_paths = ",".join(addons_dirs)

    print(Fore.WHITE + Style.BRIGHT + "First run command:" + Style.RESET_ALL + Fore.RESET)
    print("")

    print(" ".join([
        "./venv/bin/python3",
        "./odoo/odoo-bin",
        "--addons-path=%s" % addons_paths,
        "--db_host=127.0.0.1",
        "--db_port=5432",
        "--db_user=odoo",
        "--db_password=odoo",
        "--data-dir=~/data",
        "--save"
    ]))


def run():
    ts_start = datetime.datetime.now()

    print_header()

    # print_title("Configuring git")
    # git_configure()

    print_title("Parsing configuration")
    parse_config()

    print_title("Align git repositories")
    git_align()

    print_title("Preparing Python Virtualenv")
    venv_create()
    venv_requirements()

    print_title("Printing example command")
    first_run_cmd_print()

    ts_end = datetime.datetime.now()
    ts_interval = ts_end - ts_start

    print_completed(ts_interval)


if __name__ == "__main__":
    run()
