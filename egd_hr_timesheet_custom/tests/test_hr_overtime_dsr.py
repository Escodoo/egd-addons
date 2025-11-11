# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrOvertimeDsr(TransactionCase):
    """Test cases for hr.overtime.dsr model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data using class method."""
        super().setUpClass()

        # Create DSR records for testing
        cls.dsr_january = cls.env["hr.overtime.dsr"].create(
            {
                "month": "01",
                "year": "2024",
                "working_days": 22,
                "dsr_count": 8,
            }
        )

        cls.dsr_february = cls.env["hr.overtime.dsr"].create(
            {
                "month": "02",
                "year": "2024",
                "working_days": 20,
                "dsr_count": 9,
            }
        )

    def test_dsr_creation(self):
        """Test that DSR record is created correctly."""
        self.assertEqual(self.dsr_january.month, "01")
        self.assertEqual(self.dsr_january.year, "2024")
        self.assertEqual(self.dsr_january.working_days, 22)
        self.assertEqual(self.dsr_january.dsr_count, 8)

    def test_dsr_unique_month_year_constraint(self):
        """Test that duplicate month/year combination raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.env["hr.overtime.dsr"].create(
                {
                    "month": "01",
                    "year": "2024",
                    "working_days": 20,
                    "dsr_count": 10,
                }
            )
        self.assertIn("same Month and Year already exists", str(context.exception))

    def test_dsr_positive_working_days_constraint(self):
        """Test that working_days must be at least 1."""
        with self.assertRaises(ValidationError) as context:
            self.env["hr.overtime.dsr"].create(
                {
                    "month": "03",
                    "year": "2024",
                    "working_days": 0,
                    "dsr_count": 5,
                }
            )
        self.assertIn("must be at least 1", str(context.exception))

    def test_dsr_negative_working_days_constraint(self):
        """Test that negative working_days raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.env["hr.overtime.dsr"].create(
                {
                    "month": "04",
                    "year": "2024",
                    "working_days": -5,
                    "dsr_count": 5,
                }
            )
        self.assertIn("must be at least 1", str(context.exception))

    def test_dsr_positive_dsr_count_constraint(self):
        """Test that dsr_count must be at least 1."""
        with self.assertRaises(ValidationError) as context:
            self.env["hr.overtime.dsr"].create(
                {
                    "month": "05",
                    "year": "2024",
                    "working_days": 20,
                    "dsr_count": 0,
                }
            )
        self.assertIn("must be at least 1", str(context.exception))

    def test_dsr_negative_dsr_count_constraint(self):
        """Test that negative dsr_count raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.env["hr.overtime.dsr"].create(
                {
                    "month": "06",
                    "year": "2024",
                    "working_days": 20,
                    "dsr_count": -3,
                }
            )
        self.assertIn("must be at least 1", str(context.exception))

    def test_dsr_order(self):
        """Test that DSR records are ordered by year desc, month desc."""
        all_dsrs = self.env["hr.overtime.dsr"].search([])
        if len(all_dsrs) >= 2:
            # February (02) should come before January (01) when both are 2024
            feb_index = None
            jan_index = None
            for idx, dsr in enumerate(all_dsrs):
                if dsr.month == "02" and dsr.year == "2024":
                    feb_index = idx
                if dsr.month == "01" and dsr.year == "2024":
                    jan_index = idx

            if feb_index is not None and jan_index is not None:
                self.assertLess(
                    feb_index,
                    jan_index,
                    "February should come before January in descending order",
                )

    def test_dsr_required_fields(self):
        """Test that all required fields are properly set."""
        self.assertTrue(self.dsr_january.month)
        self.assertTrue(self.dsr_january.year)
        self.assertTrue(self.dsr_january.working_days)
        self.assertTrue(self.dsr_january.dsr_count)

    def test_dsr_search_by_month_year(self):
        """Test searching DSR by month and year."""
        dsr = self.env["hr.overtime.dsr"].search(
            [("month", "=", "01"), ("year", "=", "2024")], limit=1
        )
        self.assertEqual(dsr.id, self.dsr_january.id)
        self.assertEqual(dsr.working_days, 22)
        self.assertEqual(dsr.dsr_count, 8)

    def test_dsr_update_values(self):
        """Test updating DSR values."""
        self.dsr_february.write({"working_days": 21, "dsr_count": 10})
        self.assertEqual(self.dsr_february.working_days, 21)
        self.assertEqual(self.dsr_february.dsr_count, 10)

    def test_dsr_update_month_year_duplicate(self):
        """Test that updating to duplicate month/year raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.dsr_february.write({"month": "01", "year": "2024"})
