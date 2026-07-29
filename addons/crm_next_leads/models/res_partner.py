from odoo import _, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit= 'res.partner'

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