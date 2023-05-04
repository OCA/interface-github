**Odoo Modules**

.. image:: /github_connector_odoo/static/description/odoo_module_kanban.png

In each module, you can see the description of the module, the authors,
the available series, and the list of the modules that depend on the
current module.

.. image:: /github_connector_odoo/static/description/odoo_module_form.png



**Odoo Authors**

.. image:: /github_connector_odoo/static/description/odoo_author.png

This list is based on the 'author' key of the manifest file.



**Odoo License**

This list is based on the 'license' key of the manifest file.

.. image:: /github_connector_odoo/static/description/odoo_license.png



**Odoo Bin Libs**

This list is based on the 'external_dependencies' / 'bin' key of the
manifest file.

.. image:: /github_connector_odoo/static/description/odoo_bin_libs.png



**Odoo Python Libs**

This list is based on the 'external_dependencies' / 'python' key of the
manifest file.

.. image:: /github_connector_odoo/static/description/odoo_python_libs.png



**Analysis source code**

Implements Analysis source code in odoo module versions, now add new field called "has_odoo_addons" (boolean) in Analysis rule that allow (if defined) analyze odoo_module_versions and save info about it



**Soource code analysis**

Implements Source code analysis odoo module versions, now addiing new field called "has_odoo_addons" (boolean) in Analysis rule that (if defined) allows to analyze odoo_module_versions and save info about it

In 'Repository Branch' / 'Code Analysis', shows the info related to odoo_module_versions rules analysis too.



**Reporting**

This module provide a new reporting.

**Modules by Serie (and Licenses)**

.. image:: /github_connector_odoo/static/description/reporting_module_by_serie.png

**Branches/series extra options**

To use this module, you need to:

#. Go to the "Organisation Series" tab of the Organisation
#. Activate "Fetch all branches" checkbox.
#. If necessary, select the "Automatic series creation" checkbox.
#. Sync repo branches afterwards.
#. Go to branch form and select "Organization Serie" for branches
#. where it was not determined automatically.
