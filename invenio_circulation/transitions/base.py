# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation base transitions."""

from flask import current_app

from invenio_circulation.api import get_pending_loans_for_item
from invenio_circulation.errors import TransitionValidationFailed
from invenio_circulation.proxies import current_circulation


def is_pickup_at_same_library(item_pid, pickup_location_pid):
    """."""
    item_location_pid = current_app.config.get(
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    )(item_pid)
    return pickup_location_pid == item_location_pid


def should_item_be_returned(item_pid, transaction_location_pid):
    """."""
    # pending loans
    pendings = len(get_pending_loans_for_item(item_pid))
    if pendings:
        return True

    # same location
    item_location_pid = current_app.config.get(
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    )(item_pid)

    return transaction_location_pid == item_location_pid


def require_trigger(f):
    """."""
    def inner(self, loan, **kwargs):
        """."""
        trigger_name = current_app.config['CIRCULATION_TRANSITIONS_TRIGGER_NAME']
        trigger_value = self._trigger

        if trigger_name not in kwargs or kwargs.get(trigger_name) != trigger_value:
            raise TransitionValidationFailed(
                msg='No param `{0}` with value `{1}` found.'
                    .format(trigger_name, trigger_value))
        return f(self, loan, **kwargs)
    return inner


class Transition(object):
    """A transition object that is triggered on conditions."""

    def __init__(self, src, dest, permission_factory=None):
        """."""
        self.src = src
        self.dest = dest
        self.permission_factory = permission_factory

    def before(self, loan, **kwargs):
        """Evaluate conditions and raise if anything wrong."""
        if not all([self.src in current_circulation.machine.transitions,
                    self.dest in current_circulation.machine.transitions]):
            raise TransitionValidationFailed(msg='Invalid src `{0}` or dest `{1}` states'.format(self.src, self.dest))

    def update_loan(self, loan, **kwargs):
        """Update current loan with new values."""
        loan.update(kwargs)

    def execute(self, loan, **kwargs):
        """."""
        self.before(loan, **kwargs)
        self.update_loan(loan, **kwargs)
        loan['state'] = self.dest
        self.after(loan, **kwargs)

    def after(self, loan, **kwargs):
        """."""
        loan.commit()


class CallableTransition(Transition):
    """A transition object that is triggered by action name."""

    _trigger = None

    def __init__(self, src, dest, trigger, permission_factory=None):
        """."""
        super(CallableTransition, self).__init__(src, dest, permission_factory=permission_factory)
        self._trigger = trigger

    @require_trigger
    def before(self, loan, **kwargs):
        """."""
        super(CallableTransition, self).before(loan, **kwargs)

    def update_loan(self, loan, **kwargs):
        """Update current loan with new values."""
        kwargs = self.remove_extra_args(kwargs)
        super(CallableTransition, self).update_loan(loan, **kwargs)

    @property
    def trigger(self):
        """."""
        return self._trigger

    def remove_extra_args(self, kwargs):
        """."""
        kwargs.pop(current_app.config['CIRCULATION_TRANSITIONS_TRIGGER_NAME'])
        return kwargs
