from odoo.tests.common import TransactionCase


class TestAccountMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.other_user = cls.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user_egd_account_custom",
                "email": "other_user_egd_account_custom@example.com",
            }
        )

    def test_vendor_bill_gets_current_user(self):
        move = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(move.invoice_user_id, self.env.user)

    def test_vendor_bill_duplicate_gets_current_user(self):
        move = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
            }
        )
        duplicate = move.copy()
        self.assertEqual(duplicate.invoice_user_id, self.env.user)

    def test_vendor_bill_manual_salesperson_is_kept(self):
        move = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
            }
        )
        move.invoice_user_id = self.other_user
        move._compute_invoice_default_sale_person()
        self.assertEqual(move.invoice_user_id, self.other_user)

    def test_customer_invoice_behavior_unchanged(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(move.invoice_user_id, self.env.user)

        move.invoice_user_id = self.other_user
        move._compute_invoice_default_sale_person()
        self.assertEqual(move.invoice_user_id, self.other_user)
