from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestCrmNextLeads(TransactionCase):

    def test_action_create_lead_from_partner_creates_lead(self):
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        action = partner.action_create_lead_from_partner()
        lead = self.env['crm.lead'].browse(action['res_id'])
        self.assertEqual(lead.partner_id, partner)

    def test_action_create_lead_from_partner_blocks_duplicate(self):
        partner = self.env['res.partner'].create({'name': 'Test Partner 2'})
        partner.action_create_lead_from_partner()
        with self.assertRaises(UserError):
            partner.action_create_lead_from_partner()
