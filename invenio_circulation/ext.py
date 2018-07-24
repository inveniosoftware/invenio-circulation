# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for the circulation of bibliographic items."""

from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.utils import cached_property

from invenio_circulation import config
from invenio_circulation.errors import NoValidTransitionAvailable, \
    TransitionValidationFailed
from invenio_circulation.transitions.base import CallableTransition


class InvenioCirculation(object):
    """Invenio-Circulation extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.config.setdefault('RECORDS_REST_ENDPOINTS', {})
        app.config['RECORDS_REST_ENDPOINTS'].update(
            app.config['CIRCULATION_REST_ENDPOINTS'])
        app.extensions['invenio-circulation'] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('CIRCULATION_'):
                app.config.setdefault(k, getattr(config, k))

    @cached_property
    def machine(self):
        """."""
        transitions = current_app.config['CIRCULATION_LOAN_TRANSITIONS']
        return _Machine(transitions=transitions)


class _Machine(object):
    """."""

    def __init__(self, transitions):
        """."""
        self.transitions = transitions

    def _validate_current_state(self, current_state):
        """."""
        if not current_state or current_state not in self.transitions.keys():
            raise Exception

    def _get_transitions(self, current_state, trigger=None):
        """."""
        if trigger:
            return [t for t in self.transitions[current_state] if
                    isinstance(t, CallableTransition)]
        return self.transitions[current_state]

    def to_next(self, loan, **kwargs):
        """."""
        current_state = loan.get('state')
        self._validate_current_state(current_state)

        for t in self._get_transitions(current_state, kwargs.get('trigger')):
            try:
                t.execute(loan, **kwargs)
                return loan
            except TransitionValidationFailed:
                pass

        raise NoValidTransitionAvailable('No valid transition with current'
                                         ' state `{}`.'.format(current_state))
