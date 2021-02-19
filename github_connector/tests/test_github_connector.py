# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestGithubConnector(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["res.partner"]
        cls.model._need_individual_call = False

    def test_partner_get_from_id_or_create(self):
        data = {"id": "10", "name": "Mr Odoo", "url": "https://github.com"}
        partner = self.model.get_from_id_or_create(data)
        self.assertEqual(partner.name, data["name"])
        # Check create process not really create new record
        res = self.model.get_from_id_or_create(data)
        self.assertEqual(partner.id, res.id)
        # Try to archive record and try to create again
        partner.active = False
        res = self.model.get_from_id_or_create(data)
        self.assertEqual(partner.id, res.id)
