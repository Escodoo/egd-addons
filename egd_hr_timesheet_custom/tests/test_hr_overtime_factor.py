# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrOvertimeFactor(TransactionCase):
    """Test cases for hr.overtime.factor model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data using class method."""
        super().setUpClass()

        # Create overtime factors for testing
        cls.overtime_50 = cls.env["hr.overtime.factor"].create(
            {
                "name": "50% Overtime",
                "rate": 0.5,
            }
        )

        cls.overtime_100 = cls.env["hr.overtime.factor"].create(
            {
                "name": "100% Overtime",
                "rate": 1.0,
            }
        )

        cls.overtime_zero = cls.env["hr.overtime.factor"].create(
            {
                "name": "No Overtime",
                "rate": 0.0,
            }
        )

    def test_overtime_factor_creation(self):
        """Test that overtime factor is created correctly."""
        self.assertEqual(self.overtime_50.name, "50% Overtime")
        self.assertEqual(self.overtime_50.rate, 0.5)

    def test_overtime_factor_rate_50(self):
        """Test overtime factor with 50% rate."""
        self.assertEqual(self.overtime_50.rate, 0.5)

    def test_overtime_factor_rate_100(self):
        """Test overtime factor with 100% rate."""
        self.assertEqual(self.overtime_100.rate, 1.0)

    def test_overtime_factor_rate_zero(self):
        """Test overtime factor with 0% rate."""
        self.assertEqual(self.overtime_zero.rate, 0.0)

    def test_overtime_factor_required_fields(self):
        """Test that required fields are properly set."""
        self.assertTrue(self.overtime_50.name)
        self.assertIsNotNone(self.overtime_50.rate)
