# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestAccountAnalyticLine(TransactionCase):
    """Test cases for account.analytic.line overtime functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data using class method."""
        super().setUpClass()

        # Get company
        cls.company = cls.env.company

        # Get or create employee using demo data
        cls.employee = cls.env["hr.employee"].search([], limit=1)

        # Set employee costs
        cls.employee.write(
            {
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 200.0,
            }
        )

        # Get or create analytic account using demo data from same company
        cls.analytic_account = cls.env["account.analytic.account"].search(
            [("company_id", "in", [False, cls.company.id])], limit=1
        )

        # Create overtime factors
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

        # Create DSR for current month
        cls.today = date.today()
        cls.dsr_current = cls.env["hr.overtime.dsr"].create(
            {
                "month": cls.today.month,
                "year": cls.today.year,
                "working_days": 22,
                "dsr_count": 8,
            }
        )

        # Create DSR for different month
        cls.dsr_other = cls.env["hr.overtime.dsr"].create(
            {
                "month": "06",
                "year": "2024",
                "working_days": 20,
                "dsr_count": 10,
            }
        )

    def test_analytic_line_fields_exist(self):
        """Test that custom fields exist on analytic line."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 8.0,
                "date": self.today,
            }
        )

        self.assertTrue(hasattr(timesheet, "overtime_factor_id"))
        self.assertTrue(hasattr(timesheet, "overtime_dsr_id"))
        self.assertTrue(hasattr(timesheet, "overtime_rate"))
        self.assertTrue(hasattr(timesheet, "overtime_dsr_factor"))
        self.assertTrue(hasattr(timesheet, "extra_amount"))
        self.assertTrue(hasattr(timesheet, "timesheet_cost"))
        self.assertTrue(hasattr(timesheet, "timesheet_cost_overtime"))

    def test_overtime_rate_related_field(self):
        """Test that overtime_rate is correctly related to overtime_factor_id.rate."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 8.0,
                "date": self.today,
                "overtime_factor_id": self.overtime_50.id,
            }
        )

        self.assertEqual(timesheet.overtime_rate, 0.5)

    def test_onchange_overtime_dsr_sets_dsr_id(self):
        """Test that onchange sets correct DSR based on date and overtime factor."""
        timesheet = self.env["account.analytic.line"].new(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 8.0,
                "date": self.today,
                "overtime_factor_id": self.overtime_50.id,
            }
        )

        timesheet._onchange_overtime_dsr()
        self.assertEqual(timesheet.overtime_dsr_id.id, self.dsr_current.id)

    def test_onchange_overtime_dsr_no_overtime_factor(self):
        """Test that onchange does nothing when no overtime factor is set."""
        timesheet = self.env["account.analytic.line"].new(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 8.0,
                "date": self.today,
                "overtime_factor_id": False,
            }
        )

        timesheet._onchange_overtime_dsr()
        self.assertFalse(timesheet.overtime_dsr_id)

    def test_onchange_overtime_dsr_no_matching_dsr(self):
        """Test that onchange sets False when no matching DSR is found."""
        future_date = date(2099, 12, 31)
        timesheet = self.env["account.analytic.line"].new(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 8.0,
                "date": future_date,
                "overtime_factor_id": self.overtime_50.id,
            }
        )

        timesheet._onchange_overtime_dsr()
        self.assertFalse(timesheet.overtime_dsr_id)

    def test_timesheet_cost_without_overtime(self):
        """Test timesheet cost calculation without overtime."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 8.0,
                "date": self.today,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 0.0,
            }
        )

        # Test the postprocess method logic
        values = {
            "unit_amount": 8.0,
            "employee_id": self.employee.id,
            "timesheet_cost": 100.0,
        }
        result = timesheet._timesheet_postprocess_values(values)

        # Verify the result contains the calculated amount
        self.assertIn(timesheet.id, result)
        self.assertIn("amount", result[timesheet.id])

    def test_timesheet_cost_with_overtime_no_dsr(self):
        """Test timesheet cost calculation with overtime but no DSR."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet Overtime",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
                "overtime_factor_id": self.overtime_50.id,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 200.0,
            }
        )

        # Test the postprocess method logic
        values = {
            "unit_amount": 4.0,
            "employee_id": self.employee.id,
            "overtime_factor_id": self.overtime_50.id,
            "timesheet_cost_overtime": 200.0,
        }
        result = timesheet._timesheet_postprocess_values(values)

        # extra_amount = -4.0 * 200.0 * 0.5 = -400.0
        # overtime_dsr_factor = 0 (no DSR set)
        # total_amount = -400.0 + 0 = -400.0
        self.assertIn(timesheet.id, result)
        self.assertEqual(result[timesheet.id]["extra_amount"], -400.0)
        self.assertEqual(result[timesheet.id]["overtime_dsr_factor"], 0.0)
        self.assertEqual(result[timesheet.id]["amount"], -400.0)

    def test_timesheet_cost_with_overtime_and_dsr(self):
        """Test timesheet cost calculation with overtime and DSR."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet Overtime DSR",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
                "overtime_factor_id": self.overtime_100.id,
                "overtime_dsr_id": self.dsr_current.id,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 200.0,
            }
        )

        # Test the postprocess method logic
        values = {
            "unit_amount": 4.0,
            "employee_id": self.employee.id,
            "overtime_factor_id": self.overtime_100.id,
            "overtime_dsr_id": self.dsr_current.id,
            "timesheet_cost_overtime": 200.0,
        }
        result = timesheet._timesheet_postprocess_values(values)

        # extra_amount = -4.0 * 200.0 * 1.0 = -800.0
        # overtime_dsr_factor = (-800.0 / 22) * 8 = -290.909...
        # total_amount = -800.0 + (-290.909...) = -1090.909...
        self.assertIn(timesheet.id, result)
        self.assertAlmostEqual(result[timesheet.id]["extra_amount"], -800.0, places=2)
        self.assertAlmostEqual(
            result[timesheet.id]["overtime_dsr_factor"], -290.91, places=2
        )
        self.assertAlmostEqual(result[timesheet.id]["amount"], -1090.91, places=2)

    def test_timesheet_postprocess_values_no_employee(self):
        """Test that postprocess handles missing employee gracefully."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet No Employee",
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
                "overtime_factor_id": self.overtime_50.id,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 200.0,
            }
        )

        # Should not raise error, extra_amount should be 0
        self.assertEqual(timesheet.extra_amount, 0.0)

    def test_timesheet_postprocess_values_no_overtime_factor(self):
        """Test that postprocess handles missing overtime factor."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet No Factor",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 200.0,
            }
        )

        # Should not calculate overtime, extra_amount should be 0
        self.assertEqual(timesheet.extra_amount, 0.0)

    def test_timesheet_dsr_factor_with_valid_dsr(self):
        """Test DSR factor calculation with valid DSR."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
                "overtime_factor_id": self.overtime_50.id,
                "overtime_dsr_id": self.dsr_current.id,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 200.0,
            }
        )

        # Test the postprocess method logic
        values = {
            "unit_amount": 4.0,
            "employee_id": self.employee.id,
            "overtime_factor_id": self.overtime_50.id,
            "overtime_dsr_id": self.dsr_current.id,
            "timesheet_cost_overtime": 200.0,
        }
        result = timesheet._timesheet_postprocess_values(values)

        # Should calculate DSR factor with valid DSR
        self.assertIn(timesheet.id, result)
        self.assertNotEqual(result[timesheet.id]["overtime_dsr_factor"], 0.0)

    def test_timesheet_postprocess_method_exists(self):
        """Test that _timesheet_postprocess_values method exists and works."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet Update",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 0.0,
            }
        )

        # Test without overtime
        values_no_overtime = {
            "unit_amount": 4.0,
            "timesheet_cost": 100.0,
        }
        timesheet._timesheet_postprocess_values(values_no_overtime)

        # Test with overtime
        timesheet.write(
            {
                "overtime_factor_id": self.overtime_50.id,
                "overtime_dsr_id": self.dsr_current.id,
                "timesheet_cost_overtime": 200.0,
            }
        )

        values_with_overtime = {
            "unit_amount": 4.0,
            "overtime_factor_id": self.overtime_50.id,
            "overtime_dsr_id": self.dsr_current.id,
            "timesheet_cost_overtime": 200.0,
        }
        result_with_overtime = timesheet._timesheet_postprocess_values(
            values_with_overtime
        )

        # Results should be different
        self.assertIn(timesheet.id, result_with_overtime)
        self.assertIn("extra_amount", result_with_overtime[timesheet.id])
        self.assertNotEqual(result_with_overtime[timesheet.id]["extra_amount"], 0.0)

    def test_timesheet_cost_default_values(self):
        """Test that timesheet costs have default values."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet Defaults",
                "employee_id": self.employee.id,
                "account_id": self.analytic_account.id,
                "unit_amount": 4.0,
                "date": self.today,
            }
        )

        # Default should be 0.0
        self.assertEqual(timesheet.timesheet_cost, 0.0)
        self.assertEqual(timesheet.timesheet_cost_overtime, 0.0)

    def test_overtime_rate_readonly(self):
        """Test that overtime_rate is readonly (related field)."""
        field = self.env["account.analytic.line"]._fields.get("overtime_rate")
        self.assertTrue(field.readonly)

    def test_overtime_dsr_factor_readonly(self):
        """Test that overtime_dsr_factor is readonly."""
        field = self.env["account.analytic.line"]._fields.get("overtime_dsr_factor")
        self.assertTrue(field.readonly)

    def test_extra_amount_readonly(self):
        """Test that extra_amount is readonly."""
        field = self.env["account.analytic.line"]._fields.get("extra_amount")
        self.assertTrue(field.readonly)
