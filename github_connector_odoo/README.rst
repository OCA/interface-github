.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=========================================================
Analyze Odoo modules information from Github repositories
=========================================================

This module was written to extend the functionality of 'Github Connector' Module
if your repositories contain Odoo Modules.

It extends 'Analysis' features to parse code files (readme / manifest files)
and add new models and menus.

.. image:: /github_connector_odoo/static/description/menu.png

Configuration
=============

* Once installed, go to your organization, and set extra settings:

1. The name of your organization in the author keys of the manifest odoo modules
2. The URL of the file that contains IDs of your repositories for the runbot

.. image:: /github_connector_odoo/static/description/github_organization_form.png

If you had analyzed previously your repositories with the
'github Connector' module, you should launch again the Analysis Process
for all your Repository Branches.

Usage
=====

Odoo Modules
------------

.. image:: /github_connector_odoo/static/description/odoo_module_kanban.png

In each module, you can see the description of the module, the authors,
the available series, and the list of the modules that depend on the
current module.

.. image:: /github_connector_odoo/static/description/odoo_module_form.png

Odoo Authors
------------

.. image:: /github_connector_odoo/static/description/odoo_author.png

This list is based on the 'author' key of the manifest file.

Odoo License
------------

This list is based on the 'license' key of the manifest file.

.. image:: /github_connector_odoo/static/description/odoo_license.png

Odoo Bin Libs
-------------

This list is based on the 'external_dependencies' / 'bin' key of the
manifest file.

.. image:: /github_connector_odoo/static/description/odoo_bin_libs.png

Odoo Python Libs
----------------

This list is based on the 'external_dependencies' / 'python' key of the
manifest file.

.. image:: /github_connector_odoo/static/description/odoo_python_libs.png


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/229/10.0

Reporting
=========

This module provide a new reporting.

**Modules by Serie (and Licenses)**

.. image:: /github_connector_odoo/static/description/reporting_module_by_serie.png

Known issues / Roadmap
======================

Possible improvements :

* Implement deep code source analysis, like the website http://odoo-code-search.com/
  and specially:

1. Possibility to search by field or by model name. (Ex: field:invoice_id)
2. Possibility to display the number of XML, Python, Yaml, HTML, CSS lines

* Implement Social feature, like possibility to comment a module, add a
  notation, like the website https://www.odoo.com/apps

* Create a new module github_connector_odoo_website, that could display
  the modules informations for non logged users.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/interface-github/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
