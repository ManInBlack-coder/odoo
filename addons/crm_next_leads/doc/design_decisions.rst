.. _crm_next_leads_design_decisions:

Design Decisions
=================

This document tracks non-obvious design decisions made while building the
"Next Leads" feature, and the reasoning behind them. The task description
does not spell out every edge case explicitly, so decisions taken here are
recorded for transparency and for whoever reviews or maintains this module
next.

Lost leads still count as "associated"
+++++++++++++++++++++++++++++++++++++

**Decision:** A partner is considered to already have a CRM lead associated
with them even if that lead was later marked as **Lost**.

**Why this matters**

``crm.lead`` uses the standard Odoo ``active`` field (``active = fields.Boolean(...)``,
see ``addons/crm/models/crm_lead.py``) as its archive/soft-delete mechanism.
Marking a lead as Lost sets ``active = False`` rather than deleting the
record. Odoo's ORM automatically injects an implicit ``active = True`` filter
into every ``search()`` / ``_read_group()`` call unless the context
explicitly disables it via ``active_test: False``
(see ``odoo/models.py``, ``_where_calc``).

Left as the default, this means our computation of "partners who already have
a lead" would silently ignore any partner whose only lead(s) were lost,
causing them to reappear in the "Next Leads" list as if they had never been
contacted - directly contradicting the feature's purpose (avoid creating
duplicate leads for people who are already "in the system").

**Reasoning behind the choice**

The task description states the list should contain partners "that do not
have a CRM lead associated with them". The word *associated* is not
qualified by "active" or "open" - the foreign key relationship between the
lead and the partner still exists regardless of the lead's archived status.
A lost lead is still a lead that was, at some point, associated with that
partner.

**Implementation**

``models/crm_lead.py``, ``_compute_next_lead_partner_ids``:

.. code-block:: python

    self.env['crm.lead'].with_context(active_test=False)._read_group(...)

This mirrors the exact pattern already used elsewhere in the base ``crm``
module for the same reason, e.g. ``res_partner.py``'s
``_compute_opportunity_count``, which also uses
``with_context(active_test=False)`` so that lost/closed opportunities are
still counted against the partner.

**Possible alternative considered**

Leaving the default behavior (only active leads count) was considered. It
would mean a partner effectively gets "another chance" at a fresh lead once
their previous one is marked Lost. This is a legitimate business rule too,
just not the one that best matches the literal task wording, so it was not
chosen here.
