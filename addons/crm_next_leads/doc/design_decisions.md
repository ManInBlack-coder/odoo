# Design Decisions

Non-obvious decisions made while building "Next Leads", and why. The task
description leaves some edge cases open; these are recorded so the reasoning
isn't lost.

## Lost leads still count as "associated"

**What:** A partner with only a *Lost* lead is still treated as "has a
lead" - they don't reappear in "Next Leads".

**Why:** `crm.lead` uses the standard `active` field as its archive
mechanism; marking a lead Lost sets `active = False`. Odoo's ORM silently
filters `active = True` on every `search()`/`_read_group()` unless
`active_test=False` is passed. Left default, a partner whose only lead
was lost would wrongly look "leadless" again - defeating the feature's
purpose. The task says "associated", not "active", so lost leads still
count. `crm`'s own `res_partner.py` (`_compute_opportunity_count`)
makes the same choice for the same reason.

**Code** (`models/crm_lead.py`, `_compute_next_lead_partner_ids`):

```python
self.env['crm.lead'].with_context(active_test=False)._read_group(...)
```

*Alternative considered:* default (active-only) behavior, which would give
a partner "another chance" after a lost lead - a valid rule, just not the
one the task's wording best supports.

## Server-side guard against duplicate leads

**What:** `action_create_lead_from_partner` re-checks (server-side)
whether the partner already has a lead, and raises `UserError` if so.

**Why:** The "Next Leads" list is a *view* filter, not an access
restriction - any user with read access on `res.partner` could call this
method directly (RPC/`call_button`) on a partner that already has a lead,
silently defeating the whole feature. General lesson: hiding/filtering in
the client is UX, not enforcement; anything that must hold true belongs in
the method.

**Code:**

```python
existing_lead = self.env['crm.lead'].with_context(active_test=False).search(
    [('partner_id', '=', self.id)], limit=1
)
if existing_lead:
    raise UserError(_("%s already has a lead associated with them.") % self.name)
```

## Implementation note

`crm.lead.name` is `required=True` but not `precompute=True`, so Odoo
inserts it as `NULL` first and only fills it in afterwards via
`_compute_name` - which fails Postgres' immediate `NOT NULL` check.
`action_create_lead_from_partner` therefore sets `name` explicitly
(`"%s's opportunity" % self.name`, matching `_compute_name`'s own
convention) instead of relying on the compute to run in time.
