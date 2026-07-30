from datetime import timedelta

from odoo import fields, models

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    next_lead_partner_ids = fields.One2many(
        'res.partner',
        compute='_compute_next_lead_partner_ids',
        string='Next Leads',
        readonly=True,
    )

    def _compute_next_lead_partner_ids(self):
        # A partner counts as "already associated with a lead" even if that lead
        # was later marked as Lost (active=False) - see doc/design_decisions.md.
        # Partners get a "second chance" if their most recent lead is older than
        # 28 days - only a lead created within that window keeps them excluded.
        threshold = fields.Datetime.now() - timedelta(days=28)

        lead_data = self.env['crm.lead'].with_context(active_test=False)._read_group(
            domain=[('partner_id', '!=', False)],
            groupby=['partner_id'],
            aggregates=['create_date:max'],
        )
        partner_ids_with_recent_lead = [
            partner.id for partner, max_create_date in lead_data
            if max_create_date and max_create_date >= threshold
        ]

        candidate_partners = self.env['res.partner'].search(
            [('id', 'not in', partner_ids_with_recent_lead), ('partner_share', '=', True)],
            limit=50,
        )

        for lead in self:
            lead.next_lead_partner_ids = candidate_partners
        
