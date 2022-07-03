#!/venv/bin/python3

import glob
import os
import shutil

import pkg_resources

PROJECT_ADDONS_DIR: str = "project_addons"

PROJECT_ADDONS_BOOTSTRAP: list = [
    "ham_award",
    "ham_award_naval",
    "ham_repeater",
    "ham_utility",
    "widget_datetime_tz"
]

if __name__ == "__main__":
    print("Searching for all addons...")

    addons_all: dict = {}
    for file_path in glob.iglob(pathname="**", recursive=True):
        file_name: str = os.path.basename(file_path)
        if file_name != "__manifest__.py":
            continue
        if "/setup/" in file_path:
            continue
        if f"{PROJECT_ADDONS_DIR}/" in file_path:
            continue

        src: str = os.path.abspath(os.path.dirname(file_path))
        addon_name = os.path.basename(src)
        addons_all[addon_name] = src

    print(f"Found {len(addons_all)} addons")
    print()

    addons_to_parse: set = set()
    addons_to_copy: set = set()
    python_deps: set = set()

    print(f"Loading bootstrap addons:")
    for addon in PROJECT_ADDONS_BOOTSTRAP:
        print(f" - {addon}")
        addons_to_parse.add(addon)

    print()

    print(f"Searching for dependencies recursively")
    i = 0
    while len(addons_to_parse) > 0:
        i += 1
        print(f" - iter {i}: {len(addons_to_copy)} addon deps - {len(python_deps)} python deps")

        for addon in list(addons_to_parse):
            addons_to_parse.remove(addon)
            addons_to_copy.add(addon)

            if addon not in addons_all:
                raise ValueError(f"Addon {addon} not in project")

            src: str = addons_all[addon]
            manifest_path: str = os.path.join(src, "__manifest__.py")
            manifest_content: str = open(manifest_path).read()
            manifest: dict = eval(manifest_content)

            manifest_addons_depends: list = "depends" in manifest and manifest["depends"] or []
            for addon_depends in manifest_addons_depends:
                if addon_depends != "base":
                    addons_to_parse.add(addon_depends)

            manifest_python_dependencies: list = "external_dependencies" in manifest \
                                                 and "python" in manifest["external_dependencies"] \
                                                 and manifest["external_dependencies"]["python"] \
                                                 or []
            for manifest_python_dependency in manifest_python_dependencies:
                python_deps.add(manifest_python_dependency)
    print()

    addons_list = sorted(addons_to_copy, key=lambda x: x)

    print(f"Project requires only {len(addons_list)} addons:")
    for addon in addons_list:
        print(f" - {addon}")
    print()

    print(f"Project requires only {len(python_deps)} python dependencies:")
    for python_dep in python_deps:
        print(f" - {python_dep}")
    print()

    # addons_destdir_path: str = os.path.abspath(PROJECT_ADDONS_DIR)
    #
    # print("Create temporary folder")
    # if os.path.exists(addons_destdir_path):
    #     shutil.rmtree(addons_destdir_path, ignore_errors=True)
    # os.makedirs(addons_destdir_path)
    # print()
    #
    # print("Copying addons in temp folder")
    # for addon in addons_list:
    #     src: str = addons_all[addon]
    #     dest: str = os.path.join(addons_destdir_path, addon)
    #     print(f" - copying {src}")
    #     shutil.copytree(src, dest)
    # print()

    print("Preparing python dependencies")
    pydeps: dict = {}

    pydeps_odoo_lines = open("./odoo/requirements.txt").read().splitlines()
    pydeps_odoo_raw = [x for x in pkg_resources.parse_requirements(pydeps_odoo_lines)]
    for item in pydeps_odoo_raw:
        if item.marker and not item.marker.evaluate():
            continue
        name = item.name.lower()
        specs = item.specs
        pydeps[name] = specs

    for python_dep in python_deps:
        if python_dep not in pydeps:
            pydeps[python_dep] = []

    pydeps_project: list = []
    for pydep_name, pydep_specs in pydeps.items():
        spec: str = "".join([f"{pydep_spec[0]}{pydep_spec[1]}" for pydep_spec in pydep_specs])
        pydeps_project.append(f"\"{pydep_name}{spec}\"")

    print()
    print(" ".join(pydeps_project))
    print()

    print("Finish!")
