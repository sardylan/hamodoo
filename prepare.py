#!/usr/bin/python3

import glob
import os

import pkg_resources

PIP_ONLY_BINARY = [
    "poetry",
    "tomlkit",
    "pastel",
    "pygount",
    "setuptools_scm"
]


def execute(args):
    if not args:
        return

    if isinstance(args, list):
        cmd = " ".join(args)
    else:
        cmd = args

    print("\033[1;35m%s\033[0m" % cmd)
    os.system(cmd)


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

    for file_path in glob.iglob(pathname="*/**", recursive=True):
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)

        if file_name != "requirements.txt":
            continue

        if "openerp" in file_dir or "odoo" in file_dir:
            if os.path.basename(file_dir) == "doc":
                continue

        requirements_files.append(file_path)

    for requirements_file in requirements_files:
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
        args.extend([
            "--only-binary", ",".join(PIP_ONLY_BINARY)
        ])

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

    print("")
    print("")
    print("")
    print("\033[1;37mFirst run command:\033[0m")
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


def run():
    # git_configure()
    git_align()
    venv_create()
    venv_requirements()
    first_run_cmd_print()


if __name__ == "__main__":
    run()
