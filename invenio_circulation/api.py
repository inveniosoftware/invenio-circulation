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

from .errors import CirculationException, MultipleLoansOnItemError
from .pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from .search.api import search_by_patron_item, search_by_pid


class Loan(Record):
    """Loan record class."""

    pid_field = "loan_pid"
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
        resolver = Resolver(
            pid_type=CIRCULATION_LOAN_PID_TYPE,
            object_type="rec",
            getter=cls.get_record,
        )
        persistent_identifier, record = resolver.resolve(str(pid))
        return record


def is_item_available(item_pid):
    """Return True if the given item is available for loan, False otherwise."""
    config = current_app.config
    cfg_item_available = config["CIRCULATION_POLICIES"]["checkout"].get(
        "item_available"
    )
    if not cfg_item_available(item_pid):
        return False

    search = search_by_pid(item_pid=item_pid, filter_states=config.get(
        "CIRCULATION_STATES_LOAN_ACTIVE"))
    return search.execute().hits.total == 0


def get_pending_loans_by_item_pid(item_pid):
    """Return any pending loans for the given item."""
    search = search_by_pid(item_pid=item_pid, filter_states=["PENDING"])
    for result in search.scan():
        yield Loan.get_record_by_pid(result[Loan.pid_field])


def get_pending_loans_by_doc_pid(document_pid):
    """Return any pending loans for the given document."""
    search = search_by_pid(document_pid=document_pid,
                           filter_states=["PENDING"])
    for result in search.scan():
        yield Loan.get_record_by_pid(result[Loan.pid_field])


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


def get_loan_for_item(item_pid):
    """Return the Loan attached to the given item, if any."""
    loan = None
    if not item_pid:
        return

    search = search_by_pid(
        item_pid=item_pid,
        filter_states=current_app.config["CIRCULATION_STATES_LOAN_ACTIVE"]
    )

    hits = list(search.scan())
    if hits:
        if len(hits) > 1:
            raise MultipleLoansOnItemError(
                "Multiple active loans on item {0}".format(item_pid))

        loan = Loan.get_record_by_pid(hits[0][Loan.pid_field])
    return loan


def patron_has_active_loan_on_item(patron_pid, item_pid):
    """Return True if patron has a pending or active Loan for given item."""
    config = current_app.config
    if not patron_pid or not item_pid:
        raise CirculationException("Patron PID or Item PID not specified")

    search = search_by_patron_item(
        patron_pid=patron_pid,
        item_pid=item_pid,
        filter_states=['CREATED', 'PENDING'] +
        config["CIRCULATION_STATES_LOAN_ACTIVE"]
    )
    search_result = search.execute()
    return search_result.hits.total > 0
