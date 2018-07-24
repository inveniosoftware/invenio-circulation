# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation custom transitions."""

from invenio_circulation.errors import TransitionValidationFailed
from invenio_circulation.transitions.base import CallableTransition, \
    Transition, is_pickup_at_same_library, should_item_be_returned


class PendingToItemAtDesk(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(PendingToItemAtDesk, self).before(loan, **kwargs)
        if not is_pickup_at_same_library(loan['item_pid'],
                                         loan['pickup_location_pid']):
            raise TransitionValidationFailed(msg='Pickup is not in the same library.')


class PendingToItemInTransitPickup(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(PendingToItemInTransitPickup, self).before(loan, **kwargs)
        if is_pickup_at_same_library(loan['item_pid'],
                                     loan['pickup_location_pid']):
            raise TransitionValidationFailed(msg='Pickup in the same library.')


class ItemOnLoanToItemInTransitHouse(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(ItemOnLoanToItemInTransitHouse, self).before(loan, **kwargs)
        if should_item_be_returned(loan['item_pid'],
                                   kwargs.get('transaction_location_pid')):
            raise TransitionValidationFailed(msg='Item should be returned.')


class ItemOnLoanToItemReturned(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(ItemOnLoanToItemReturned, self).before(loan, **kwargs)
        if not should_item_be_returned(loan['item_pid'],
                                       kwargs.get('transaction_location_pid')):
            raise TransitionValidationFailed(msg='Item should be in transit in house.')


class CreatedToPending(CallableTransition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(CreatedToPending, self).before(loan, **kwargs)
        if not kwargs.get('pickup_location_pid'):
            raise TransitionValidationFailed(msg='Pickup location is required')
