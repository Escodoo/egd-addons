# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrEmployee(TransactionCase):
    """Test cases for hr.employee timesheet cost fields."""

    @classmethod
    def setUpClass(cls):
        """Set up test data using class method."""
        super().setUpClass()

        # Use demo employee if available, otherwise create minimal one
        cls.employee = cls.env["hr.employee"].search([], limit=1)

        # Get company currency
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id

    def test_employee_timesheet_cost_field_exists(self):
        """Test that timesheet_cost field exists on employee."""
        self.assertTrue(hasattr(self.employee, "timesheet_cost"))

    def test_employee_timesheet_cost_overtime_field_exists(self):
        """Test that timesheet_cost_overtime field exists on employee."""
        self.assertTrue(hasattr(self.employee, "timesheet_cost_overtime"))

    def test_employee_set_timesheet_cost(self):
        """Test setting timesheet_cost on employee."""
        self.employee.write({"timesheet_cost": 100.0})
        self.assertEqual(self.employee.timesheet_cost, 100.0)

    def test_employee_set_timesheet_cost_overtime(self):
        """Test setting timesheet_cost_overtime on employee."""
        self.employee.write({"timesheet_cost_overtime": 150.0})
        self.assertEqual(self.employee.timesheet_cost_overtime, 150.0)

    def test_employee_set_both_costs(self):
        """Test setting both timesheet costs on employee."""
        self.employee.write(
            {
                "timesheet_cost": 100.0,
                "timesheet_cost_overtime": 150.0,
            }
        )
        self.assertEqual(self.employee.timesheet_cost, 100.0)
        self.assertEqual(self.employee.timesheet_cost_overtime, 150.0)

    def test_employee_timesheet_cost_default_value(self):
        """Test that timesheet costs can be zero or False."""
        employee = self.env["hr.employee"].create({"name": "Test Employee 2"})
        # Fields should exist even if not set
        self.assertIsNotNone(employee.timesheet_cost)
        self.assertIsNotNone(employee.timesheet_cost_overtime)

    def test_employee_timesheet_cost_tracking(self):
        """Test that timesheet_cost has tracking enabled."""
        field = self.env["hr.employee"]._fields.get("timesheet_cost")
        self.assertTrue(field.tracking)

    def test_employee_timesheet_cost_overtime_tracking(self):
        """Test that timesheet_cost_overtime has tracking enabled."""
        field = self.env["hr.employee"]._fields.get("timesheet_cost_overtime")
        self.assertTrue(field.tracking)
