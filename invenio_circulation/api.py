# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from flask import current_app
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from .search import LoansSearch


class Loan(Record):
    """Loan record class."""

    _schema = "loans/loan-v1.0.0.json"

    def __init__(self, data, model=None):
        """."""
        self["state"] = current_app.config["CIRCULATION_LOAN_INITIAL_STATE"]
        super(Loan, self).__init__(data, model)

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create Loan record."""
        data["$schema"] = current_jsonschemas.path_to_url(cls._schema)
        return super(Loan, cls).create(data, id_=id_, **kwargs)

    @classmethod
    def get_record_by_pid(cls, pid, with_deleted=False):
        """Get ils record by pid value."""
        from .config import _CIRCULATION_LOAN_PID_TYPE
        resolver = Resolver(
            pid_type=_CIRCULATION_LOAN_PID_TYPE,
            object_type="rec",
            getter=cls.get_record,
        )
        persistent_identifier, record = resolver.resolve(str(pid))
        return record


def is_item_available(item_pid):
    """."""
    config = current_app.config
    cfg_item_available = config["CIRCULATION_POLICIES"]["checkout"].get(
        "item_available"
    )
    if not cfg_item_available(item_pid):
        return False

    if any(
        True
        for loan in LoansSearch.search_loans_by_pid(
            item_pid=item_pid,
            exclude_states=config.get("CIRCULATION_STATES_ITEM_AVAILABLE"),
        )
    ):
        return False
    return True


def get_pending_loans_by_item_pid(item_pid):
    """."""
    for result in LoansSearch.search_loans_by_pid(
        item_pid=item_pid, filter_states=["PENDING"]
    ):
        yield Loan.get_record_by_pid(result["loanid"])


def get_pending_loans_by_doc_pid(document_pid):
    """."""
    for result in LoansSearch.search_loans_by_pid(
        document_pid=document_pid, filter_states=["PENDING"]
    ):
        yield Loan.get_record_by_pid(result["loanid"])


def get_available_item_by_doc_pid(document_pid):
    """Returns an item pid available for this document."""
    for item_pid in get_items_by_doc_pid(document_pid):
        if is_item_available(item_pid):
            return item_pid
    return None


def get_items_by_doc_pid(document_pid):
    """Returns a list of item pids for this document."""
    return current_app.config["CIRCULATION_ITEMS_RETRIEVER_FROM_DOCUMENT"](
        document_pid
    )


def get_document_by_item_pid(item_pid):
    """Return the document pid of this item_pid."""
    return current_app.config["CIRCULATION_DOCUMENT_RETRIEVER_FROM_ITEM"](
        item_pid
    )
