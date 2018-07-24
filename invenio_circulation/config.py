# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for the circulation of bibliographic items."""

from .api import Loan
from .transitions.base import CallableTransition, Transition
from .transitions.transitions import ItemOnLoanToItemInTransitHouse, \
    ItemOnLoanToItemReturned, PendingToItemAtDesk, \
    PendingToItemInTransitPickup
from .utils import is_checkin_valid, is_checkout_valid, is_request_valid, \
    is_request_validate_valid, item_location_retriever

CIRCULATION_LOAN_TRANSITIONS = {
    'CREATED': [
        CallableTransition(src='CREATED', dest='PENDING', trigger='request'),
        CallableTransition(src='CREATED', dest='ITEM_ON_LOAN',
                           trigger='checkout')
    ],
    'PENDING': [
        PendingToItemAtDesk(src='PENDING', dest='ITEM_AT_DESK'),
        PendingToItemInTransitPickup(src='PENDING',
                                     dest='ITEM_IN_TRANSIT_FOR_PICKUP'),
        CallableTransition(src='PENDING', dest='CANCELLED',
                           trigger='cancel')
    ],
    'ITEM_AT_DESK': [
        Transition(src='ITEM_AT_DESK', dest='ITEM_ON_LOAN'),
        CallableTransition(src='ITEM_AT_DESK', dest='CANCELLED',
                           trigger='cancel')
    ],
    'ITEM_IN_TRANSIT_FOR_PICKUP': [
        Transition(src='ITEM_IN_TRANSIT_FOR_PICKUP', dest='ITEM_AT_DESK'),
        CallableTransition(src='ITEM_IN_TRANSIT_FOR_PICKUP', dest='CANCELLED',
                           trigger='cancel')
    ],
    'ITEM_ON_LOAN': [
        ItemOnLoanToItemInTransitHouse(src='ITEM_ON_LOAN',
                                       dest='ITEM_IN_TRANSIT_TO_HOUSE'),
        ItemOnLoanToItemReturned(src='ITEM_ON_LOAN', dest='ITEM_RETURNED'),
        CallableTransition(src='ITEM_ON_LOAN', dest='CANCELLED',
                           trigger='cancel')
    ],
    'ITEM_IN_TRANSIT_TO_HOUSE': [
        Transition(src='ITEM_IN_TRANSIT_TO_HOUSE', dest='ITEM_RETURNED'),
        CallableTransition(src='ITEM_IN_TRANSIT_TO_HOUSE', dest='CANCELLED',
                           trigger='cancel')
    ],
    'ITEM_RETURNED': [],
    'CANCELLED': [],
}
"""."""

CIRCULATION_LOAN_INITIAL_STATE = 'CREATED'
"""."""

CIRCULATION_TRANSITIONS_TRIGGER_NAME = 'trigger'
"""."""

CIRCULATION_ITEM_LOCATION_RETRIEVER = item_location_retriever
"""."""

CIRCULATION_DEFAULT_REQUEST_DURATION = 30
"""."""

CIRCULATION_DEFAULT_LOAN_DURATION = 30
"""."""

CIRCULATION_POLICIES = dict(
    checkout=is_checkout_valid,
    checkin=is_checkin_valid,
    request=is_request_valid,
    validate_request=is_request_validate_valid,
)
"""."""

_CIRCULATION_LOAN_PID_TYPE = 'loan_pid'
"""."""

_CIRCULATION_LOAN_MINTER = 'loan_pid'
"""."""

_CIRCULATION_LOAN_FETCHER = 'loan_pid'
"""."""

CIRCULATION_REST_ENDPOINTS = dict(
    loan_pid=dict(
        pid_type=_CIRCULATION_LOAN_PID_TYPE,
        pid_minter=_CIRCULATION_LOAN_MINTER,
        pid_fetcher=_CIRCULATION_LOAN_FETCHER,
        # search_class=RecordsSearch,
        # indexer_class=RecordIndexer,
        search_index=None,
        search_type=None,
        record_class=Loan,
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
        },
        list_route='/circulation/loan/',
        item_route='/circulation/loan/<pid(loan_pid):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
    ),
)
"""."""
