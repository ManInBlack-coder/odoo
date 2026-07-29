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
        lead_data = self.env['crm.lead'].with_context(active_test=False)._read_group(
            domain=[('partner_id', '!=', False)],
            groupby=['partner_id'],
            aggregates=['__count'],
        )
        partner_ids_with_lead = [partner.id for partner, count in lead_data]

        leadless_partners = self.env['res.partner'].search(
            [('id', 'not in', partner_ids_with_lead)],
            limit=50,
        )

        for lead in self:
            lead.next_lead_partner_ids = leadless_partners
        
