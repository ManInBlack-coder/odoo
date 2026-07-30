from odoo import _, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit= 'res.partner'

    last_lead_create_date = fields.Datetime(
        compute='_compute_last_lead_create_date',
        string='Last Lead Date',
        help="Creation date of this partner's most recent lead (including lost ones). "
             "Empty if the partner has never had a lead at all.",
    )

    def _compute_last_lead_create_date(self):
        lead_data = self.env['crm.lead'].with_context(active_test=False)._read_group(
            domain=[('partner_id', 'in', self.ids)],
            groupby=['partner_id'],
            aggregates=['create_date:max'],
        )
        last_date_by_partner = {partner.id: max_create_date for partner, max_create_date in lead_data}
        for partner in self:
            partner.last_lead_create_date = last_date_by_partner.get(partner.id, False)

    def action_create_lead_from_partner(self):
        self.ensure_one()
        existing_lead = self.env['crm.lead'].with_context(active_test=False).search(
            [('partner_id', '=', self.id)], limit=1
        )
        if existing_lead:
            raise UserError(_("%s already has a lead associated with them.") % self.name)

        lead = self.env['crm.lead'].create({
            'name': "%s's opportunity" % self.name,
            'partner_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': lead.id,
            'target': 'current',
        }