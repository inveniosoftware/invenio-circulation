# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2020 CERN.
# Copyright (C) 2018-2022 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for the circulation of bibliographic items."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "mock>=2.0.0",
    "pytest-invenio>=2.0.0,<2.2.0",
    "pytest-mock>=1.6.0",
    "celery>=4.4.0,<5.3",  # Temporary, until fixed in `pytest-invenio`
    "invenio-app>=1.3.1",
    "invenio-jsonschemas>=1.0.1",
    "Flask>=2.2.0,<2.3.0",
]

invenio_db_version = "1.1.0,<1.2.0"
invenio_search_version = "2.1.0,<3.0.0"

extras_require = {
    "elasticsearch7": [
        "invenio-search[elasticsearch7]>={}".format(invenio_search_version),
        # unsupported ES version issue
        "elasticsearch>=7.0.0,<7.14",
    ],
    "opensearch1": [
        "invenio-search[opensearch1]>={}".format(invenio_search_version),
        "opensearch-py>=1.1.0,<2.0.0"
    ],
    "opensearch2": [
        "invenio-search[opensearch2]>={}".format(invenio_search_version),
        "opensearch-py>=2.0.0,<3.0.0"
    ],
    "docs": [
        "Sphinx>=4.2.0",
    ],
    "mysql": ["invenio-db[mysql,versioning]>={}".format(invenio_db_version)],
    "postgresql": [
        "invenio-db[postgresql,versioning]>={}".format(invenio_db_version)
    ],
    "sqlite": ["invenio-db[versioning]>={}".format(invenio_db_version)],
    "tests": tests_require,
}

extras_require["all"] = []
for name, reqs in extras_require.items():
    if name in (
        "mysql",
        "postgresql",
        "sqlite",
        "elasticsearch7",
        "opensearch1",
        "opensearch2",
    ):
        continue
    extras_require["all"].extend(reqs)

setup_requires = ["Babel>=2.8"]

install_requires = [
    "arrow>=0.15.0",
    "invenio-access>=2.0.0,<3.0.0",
    "invenio-indexer>=2.2.0,<3.0.0",
    "invenio-logging>=1.0.0,<3.0.0",
    "invenio-pidstore>=1.3.0,<1.4.0",
    "invenio-records-rest>=2.2.0,<2.3.0",
    "invenio-jsonschemas>=1.1.4,<1.2.0"
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_circulation", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-circulation",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio",
    license="MIT",
    author="CERN",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/invenio-circulation",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    python_requires=">=3",
    entry_points={
        "invenio_base.apps": [
            "invenio_circulation = invenio_circulation:InvenioCirculation"
        ],
        "invenio_base.api_apps": [
            "invenio_circulation = invenio_circulation:InvenioCirculation"
        ],
        "invenio_base.api_blueprints": [
            "invenio_circulation_loan_actions = "
            "invenio_circulation.views:create_loan_actions_blueprint",
            "invenio_circulation_loan_replace_item = "
            "invenio_circulation.views:create_loan_replace_item_blueprint",
        ],
        "invenio_i18n.translations": ["messages = invenio_circulation"],
        "invenio_pidstore.fetchers": [
            "loanid = invenio_circulation.pidstore.fetchers:loan_pid_fetcher"
        ],
        "invenio_pidstore.minters": [
            "loanid = invenio_circulation.pidstore.minters:loan_pid_minter"
        ],
        "invenio_jsonschemas.schemas": ["loans = invenio_circulation.schemas"],
        "invenio_search.mappings": ["loans = invenio_circulation.mappings"],
        "invenio_records.jsonresolver": [
            "item_resolver = invenio_circulation.records.jsonresolver.item",
            "patron_resolver = invenio_circulation.records.jsonresolver.patron",
            "document_resolver = invenio_circulation.records.jsonresolver.document",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 1 - Planning",
    ],
)
