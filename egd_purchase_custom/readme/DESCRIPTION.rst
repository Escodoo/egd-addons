This module extends the standard Odoo Purchase App Odoo, adding some functionalities:

Added Fields
------------

- **egd_target_value** (Float)
  Stores the target unit price value. This value is automatically calculated based on various criteria including purchase requests and analytic accounts.

- **egd_target_above** (Boolean)
  Indicates whether the unit price of the order line is above the target price. This field is automatically calculated and helps to monitor if the prices are as expected.

Added Calculations and Business Logic
-------------------------------------

1. **Target Value Calculation (egd_target_value)**
   The system calculates the target value by considering information from products and services in blanket sales orders and associated analytic accounts. The unit price is adjusted according to the match found.

2. **Determining Target Above (egd_target_above)**
   Based on the target value and the current unit price, the system determines whether the price is above the target value. This information is crucial for purchasing decisions.

Added View Customizations
-------------------------

- The `account_analytic_id` field is made mandatory in the purchase order line. This ensures that each purchase order line has a linked analytic account, facilitating more accurate financial tracking and reporting.
