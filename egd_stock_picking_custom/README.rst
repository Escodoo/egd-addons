========================
Egd Stock Picking Custom
========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:5e7c36336699b480bd737604deeafc43dd7700a0f052023c120f0dbd22011ed0
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fegd--addons-lightgray.png?logo=github
    :target: https://github.com/OCA/egd-addons/tree/14.0/egd_stock_picking_custom
    :alt: OCA/egd-addons
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/egd-addons-14-0/egd-addons-14-0-egd_stock_picking_custom
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/egd-addons&target_branch=14.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

EGD Custody Report

The equipment loan report for partners and employees has been implemented.

When an employee requests equipment, the report includes the information contained therein, such as the requester's details and information about the requested equipment.

For material loans to partners, it is necessary to specify the employee responsible for the custody, as they will also be responsible for delivering the materials. Consequently, the report includes information about the individual responsible for delivering the materials to the partner and details of the products delivered.

The report is accessible via the 'Print' button with the label 'EGD Custody.' After selecting this option, the report will be printed with the data contained in the picking.

**Table of contents**

.. contents::
   :local:

Usage
=====

Inventory Definitions
    - Traceability
    - Lot/Serial Numbers
    - Expiration Date
    - Display Lot & Serial Numbers on Delivery Receipts
    - Display Expiration Dates on Delivery Receipts

User Permissions
    - Analytical Accounting
    - Display serial and lot numbers on delivery notes
    - Include expiration dates on delivery notes

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/egd-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/egd-addons/issues/new?body=module:%20egd_stock_picking_custom%0Aversion:%2014.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Escodoo

Contributors
~~~~~~~~~~~~

* `Escodoo <https://www.escodoo.com.br>`_:

  * Marcel Savegnago <marcel.savegnago@escodoo.com.br>
  * Rodrigo Trindade <rodrigo.trindade@escodoo.com.br>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/egd-addons <https://github.com/OCA/egd-addons/tree/14.0/egd_stock_picking_custom>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
