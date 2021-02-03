#!/usr/bin/python3
#
# Prepare script for Odoo Installation
#
# Version changelog:
#
# 4. Adds support to check for venv only outside git repository
# 3. Check import dependencies
# 2. Adds local configuration file
# 1. First implementation
#

import datetime
import glob
import json
import os
import subprocess
import sys

import pkg_resources

try:
    from colorama import Fore, Style
except Exception:
    print("Cannot import \"colorama\"")
    print("Please execute as root: \"apt install python3-colorama\"")
    sys.exit(-1)

PREPARE_VERSION = 4

PREPARE_CONFIG_FILE_PROJECT = "__prepare__.json"
PREPARE_CONFIG_FILE_LOCAL = ".prepare.json"


def exit_error(error_code: int = -1, message: str = ""):
    print()
    print(Fore.LIGHTRED_EX + Style.BRIGHT + "ERROR!!!" + Style.RESET_ALL + Fore.RESET)
    print(Fore.LIGHTRED_EX + ("Exit code: %d" % error_code) + Fore.RESET)

    if message:
        print(Fore.LIGHTRED_EX + message + Fore.RESET)

    print()

    sys.exit(error_code)


def execute(args: list, skip_error: bool = False, cwd: str = ".", env: dict = None):
    if not args:
        return

    if env is None:
        env = {}

    print()
    print()
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    $ " + " ".join(args) + Style.RESET_ALL + Fore.RESET)
    print()

    extra = {}

    if cwd:
        extra["cwd"] = cwd

    if len(env) > 0:
        extra["env"] = env

    pr = subprocess.run(args=args, **extra)
    cmd_result = pr.returncode

    print()

    if not skip_error and cmd_result != 0:
        exit_error(cmd_result)


def env_prepend(key, value):
    items = []

    if key in os.environ:
        items.extend([x.strip() for x in os.environ[key].split(":") if x.strip()])

    items.insert(0, value)

    os.environ[key] = ":".join(items)


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


def print_title(title: str = ""):
    print(Fore.LIGHTRED_EX + Style.BRIGHT + title + Style.RESET_ALL + Fore.RESET)
    print()


def print_step(message: str = ""):
    if not message:
        return

    print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "    " + message + Style.RESET_ALL + Fore.RESET)
    print()


def print_completed(ts_duration):
    print()
    print(Fore.LIGHTRED_EX + "completed!!" + Fore.RESET)
    print()
    print("Duration: " + Fore.LIGHTBLUE_EX + str(ts_duration) + Fore.RESET)
    print()
    print()
    print()


class Preparer:
    def __init__(self):
        self._pip_only_binary: list = []
        self._pip_constraints_files: list = []
        self._pip_overrides: list = []

    def run(self):
        ts_start = datetime.datetime.now()

        print_header()

        self._parse_config(PREPARE_CONFIG_FILE_PROJECT)
        self._parse_config(PREPARE_CONFIG_FILE_LOCAL)

        # self._git_configure()
        self._git_align()

        self._venv_create()
        self._venv_requirements()

        self._first_run_cmd_print()

        ts_end = datetime.datetime.now()
        ts_interval = ts_end - ts_start

        print_completed(ts_interval)

    def _parse_config(self, filepath: str):
        if not os.path.exists(filepath):
            return

        print_title("Parsing configuration %s" % filepath)

        fd = open(filepath, "r")
        raw_content = fd.read()
        fd.close()

        config_data = json.loads(raw_content)

        if "python_dir" in config_data:
            python_dir = config_data["python_dir"]

            env_prepend("PATH", "%s/bin" % python_dir)

        if "only_binary" in config_data:
            for item in config_data["only_binary"]:
                self._pip_only_binary.append(item)

        if "constraint_files" in config_data:
            for item in config_data["constraint_files"]:
                self._pip_constraints_files.append(item)

        if "overrides" in config_data:
            for item in config_data["overrides"]:
                self._pip_overrides.append(item)

    def _git_configure(self):
        print_title("Configuring git")
        execute(["git", "config", "--global", "credential.helper", "\"cache --timeout=300\""])

    def _git_align(self):
        print_title("Align git repositories")

        if not os.path.isdir(".git"):
            print("Skipping 'cause we are not inside a git repo")
            return

        execute(["git", "submodule", "init"])
        execute(["git", "submodule", "update"])

    def _venv_create(self):
        print_title("Preparing Python Virtualenv")

        if os.path.isdir("venv"):
            return

        execute(["python3", "-m", "venv", "venv"])

    def _venv_requirements(self):
        print_title("Installing Venv requirements")

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

        for override in self._pip_overrides:
            override_parsed_reqs = pkg_resources.parse_requirements(override)
            items = [x for x in override_parsed_reqs]
            if not items:
                continue

            item = items[0]
            if item.marker and not item.marker.evaluate():
                continue

            if not item.specs:
                continue

            if item.name in reqs:
                reqs[item.name] = item.specs[0][1]

        reqs["Cython"] = None

        reqs = sorted(reqs.items(), key=lambda x: x[0])

        reqs_args = [value and "%s==%s" % (key, value) or key for key, value in reqs]
        if not reqs_args:
            return

        args = [
            "./venv/bin/pip3",
            "install",
            "--no-binary", ":all:"
        ]

        if self._pip_only_binary:
            args.extend(["--only-binary", ",".join(self._pip_only_binary)])

        for item in self._pip_constraints_files:
            args.extend(["--constraint", item])

        args.extend(reqs_args)

        execute(args)

    def _first_run_cmd_print(self):
        print_title("Printing example command")

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


if __name__ == "__main__":
    preparer = Preparer()
    preparer.run()
