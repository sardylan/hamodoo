#!/usr/bin/python3
#
# Prepare script for Odoo Installation
#
# Version changelog:
#
# 14. Adds flags for skipping venv checks
# 13. Adds upgrade of pip and setuptools utilities in virtualenv
# 12. Case insensitiveness for dependency management
# 11. Implements logic for dependency version management (grater-than, lesser-than, etc.)
# 10. Adds command for development
# 9.  Removing skeleton from addons-path and adds flag for git configure
# 8.  Adds command line args
# 7.  Adds alphabetical sorting for "--addons-path" parameter
# 6.  Adds Python version check
# 5.  Adds support for installation of 3rd-parties libraries
# 4.  Adds support to check for venv only outside git repository
# 3.  Check import dependencies
# 2.  Adds local configuration file
# 1.  First implementation

import argparse
import datetime
import glob
import json
import os
import subprocess
import sys

import pkg_resources

if sys.version_info < (3, 6):
    print("This script requires Python version at least 3.6")
    sys.exit(-1)

try:
    from colorama import Fore, Style
except Exception:
    print("Cannot import \"colorama\"")
    print("Please execute as root: \"apt install python3-colorama\"")
    sys.exit(-2)

SCRIPT_TITLE: str = "Prepare"
SCRIPT_VERSION: int = 14

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
          + f"{SCRIPT_TITLE} script version "
          + Style.RESET_ALL + Fore.RESET
          + Fore.LIGHTBLUE_EX + Style.BRIGHT
          + f"{SCRIPT_VERSION}"
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


STEP_PARSE_CONFIG = "parse_config"
STEP_CONFIGURE_GIT = "configure_git"
STEP_GIT_ALIGN = "git_align"
STEP_VENV = "venv"
STEP_ODOO_CMDLINE = "odoo_cmdline"


class Preparer:
    def __init__(self, steps: dict):
        self._steps: dict = steps

        self._pip_only_binary: list = []
        self._pip_constraints_files: list = []
        self._pip_overrides: list = []

    def run(self):
        ts_start = datetime.datetime.now()

        print_header()

        if self._steps[STEP_PARSE_CONFIG]:
            self._parse_config(PREPARE_CONFIG_FILE_PROJECT)
            self._parse_config(PREPARE_CONFIG_FILE_LOCAL)

        if self._steps[STEP_CONFIGURE_GIT]:
            self._git_configure()

        if self._steps[STEP_GIT_ALIGN]:
            if os.path.isdir(".git"):
                self._git_align()

        if self._steps[STEP_VENV]:
            self._venv_create()
            self._venv_pip_upgrade()
            self._venv_requirements()

            if os.path.isdir("./3rd-parties"):
                self._venv_3rdparties()

        if self._steps[STEP_ODOO_CMDLINE]:
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

        execute(["git", "submodule", "init"])
        execute(["git", "submodule", "update"])

    def _venv_create(self):
        print_title("Preparing Python Virtualenv")

        if os.path.isdir("venv"):
            return

        execute(["python3", "-m", "venv", "venv"])

    def _venv_pip_upgrade(self):
        print_title("Upgrading Venv pip and setuptools")

        execute(["./venv/bin/pip3", "install", "--upgrade", "pip", "setuptools"])

    def _venv_requirements(self):
        print_title("Installing Venv requirements")

        requirements_files: list = []

        files_reqs: dict = {}

        for file_path in glob.iglob(pathname="**", recursive=True):
            file_name: str = os.path.basename(file_path)
            file_dir: str = os.path.dirname(file_path)

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

                item_name = item.name.lower()

                if item_name not in files_reqs:
                    files_reqs[item_name] = []

                files_reqs[item_name].extend(item.specs)

        resolve_reqs: dict = {}

        for dep, vers in files_reqs.items():
            if dep not in resolve_reqs:
                resolve_reqs[dep]: list = [False, False, False]

            for ver in vers:
                ver_op = ver[0]
                ver_version = ver[1]

                if ">" in ver_op:
                    if not resolve_reqs[dep][0]:
                        resolve_reqs[dep][0] = ver_version
                    elif pkg_resources.parse_version(ver_version) > pkg_resources.parse_version(resolve_reqs[dep][0]):
                        resolve_reqs[dep][0] = ver_version

                if "=" in ver_op:
                    if not resolve_reqs[dep][1]:
                        resolve_reqs[dep][1] = ver_version
                    elif pkg_resources.parse_version(ver_version) > pkg_resources.parse_version(resolve_reqs[dep][1]):
                        resolve_reqs[dep][1] = ver_version

                if "<" in ver_op:
                    if not resolve_reqs[dep][2]:
                        resolve_reqs[dep][2] = ver_version
                    elif pkg_resources.parse_version(ver_version) < pkg_resources.parse_version(resolve_reqs[dep][2]):
                        resolve_reqs[dep][2] = ver_version

        reqs: dict = {}

        for dep_name, version_list in resolve_reqs.items():
            vgt = version_list[0]
            veq = version_list[1]
            vlt = version_list[2]

            version_final = False

            if vgt and not veq and not vlt:
                version_final = f">{vgt}"
            elif not vgt and veq and not vlt:
                version_final = f"=={veq}"
            elif vgt and veq and not vlt:
                if pkg_resources.parse_version(vgt) == pkg_resources.parse_version(veq):
                    version_final = f">={vgt}"
                else:
                    version_final = f">{vgt}<={veq}"
            elif not vgt and not veq and vlt:
                version_final = f"<{vlt}"
            elif vgt and not veq and vlt:
                version_final = f">{vgt}<{vlt}"
            elif not vgt and veq and vlt:
                if pkg_resources.parse_version(veq) == pkg_resources.parse_version(vlt):
                    version_final = f"<={vlt}"
                else:
                    version_final = f">={veq}<{vlt}"
            elif vgt and veq and vlt:
                if pkg_resources.parse_version(veq) == pkg_resources.parse_version(vgt):
                    version_final = f">={vgt}<{vlt}"
                elif pkg_resources.parse_version(veq) == pkg_resources.parse_version(vlt):
                    version_final = f">{vgt}<={vlt}"
                else:
                    version_final = f">{vgt}<{vlt}"

            reqs[dep_name] = version_final

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
                reqs[item.name] = f"=={item.specs[0][1]}"

        if "Cython" not in reqs:
            reqs["Cython"] = None

        if "setuptools" not in reqs:
            reqs["setuptools"] = None

        reqs = sorted(reqs.items(), key=lambda x: x[0])

        reqs_args = [value and "%s%s" % (key, value) or key for key, value in reqs]
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

    def _venv_3rdparties(self):
        print_title("Installing 3rd-parties libraries in venv")

        for libdir in glob.iglob(pathname="./3rd-parties/*", recursive=False):
            print_step(f"Parsing library \"{libdir}\"")

            setup_file = os.path.abspath(os.path.join(libdir, "setup.py"))
            if not os.path.exists(setup_file):
                print("setup.py not found, skipping")

            abs_python = os.path.abspath("./venv/bin/python3")
            cwd = os.path.abspath(libdir)

            args = [
                abs_python,
                setup_file,
                "install"
            ]

            execute(args=args, cwd=cwd)

        print()

    def _first_run_cmd_print(self):
        print_title("Printing example command")
        custom_addons_dirs = []
        addons_dirs = [
            "odoo/addons",
            "odoo/odoo/addons"
        ]

        for file_path in glob.iglob(pathname="*/*/*", recursive=True):
            file_name = os.path.basename(file_path)
            if file_name != "__manifest__.py":
                continue

            file_dir = os.path.dirname(file_path)
            module_dir = os.path.dirname(file_dir)
            if "test" in module_dir:
                continue
            if module_dir in ["skeleton"]:
                continue

            if module_dir not in custom_addons_dirs:
                custom_addons_dirs.append(module_dir)

        custom_addons_dirs.sort()
        addons_dirs.extend(custom_addons_dirs)
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

        print("")
        print("")
        print("")
        print(Fore.WHITE + Style.BRIGHT + "For DEVELOPMENT:" + Style.RESET_ALL + Fore.RESET)
        print("")

        print("\n".join([
            "--http-port=8069",
            "--limit-time-cpu=9999999",
            "--limit-time-real=9999999",
            "--addons-path=%s" % addons_paths,
            "--load=web",
            "--workers=0",
            "--db_host=127.0.0.1",
            "--db_port=5432",
            "--db_user=odoo",
            "--db_password=odoo",
            "",
            "--database=odoo",
            "--update=app"
        ]))

        print("")
        print(Fore.LIGHTYELLOW_EX + "Last two lines are intended only FOR UPDATE" + Fore.RESET)


if __name__ == "__main__":
    steps: dict = {
        STEP_PARSE_CONFIG: True,
        STEP_CONFIGURE_GIT: False,
        STEP_GIT_ALIGN: True,
        STEP_VENV: True,
        STEP_ODOO_CMDLINE: True
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--configure-git", help="Configure global params for git", action="store_true")
    parser.add_argument("-c", "--only-cmdline", help="Display only Odoo command line example", action="store_true")
    parser.add_argument("-s", "--skip-venv", help="Skip Python Virtualenv checks and creation", action="store_true")

    args = parser.parse_args()

    if args.configure_git:
        steps[STEP_CONFIGURE_GIT] = True

    if args.skip_venv:
        steps[STEP_VENV] = False

    if args.only_cmdline:
        steps[STEP_PARSE_CONFIG] = False
        steps[STEP_CONFIGURE_GIT] = False
        steps[STEP_GIT_ALIGN] = False
        steps[STEP_VENV] = False
        steps[STEP_ODOO_CMDLINE] = True

    preparer = Preparer(steps)
    preparer.run()
