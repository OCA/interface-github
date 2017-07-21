.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

======================================
Load Github Data in your Odoo Instance
======================================

This module allow you to

* recover social informations from Github. (Members of organizations,
  Pull Requests, Issues, Comments, ...)
* download source code from Github

Configuration
=============

Once installed, you have to:

* Open your openerp.cfg file and add extra settings to mention github
  credentials, adding the following entries

github_login = your_github_login
github_password = your_github_password

* go to 'Settings' / 'Technical' / 'Parameters' / 'System Parameters'
    * github.max_try: mention the number of call to the API, before an error
      is raised. Set an high value if your connection is bad
    * git.source_code_loca_path: set a local folder, that will be used to
      download source code from github
    * git.partial_commit_during_analyze: Set to True if you want to commit
      in the database the result of the analysis after each repository analysis.
      Set to True if you have a lot of repository to reduce the size of
      the transaction, when you realize the first big analyse.

.. image:: /github_connector/static/description/github_settings.png

* Go to your(s) user(s) form to put them in the new 'Connector Github Manager'
  groups. The members of this group will have the possibility to run Github
  synchronization.

Usage
=====

To recover information from github, you have to:

* go to 'Github' / 'Settings' / 'Sync Object'
* Select the object type you want to synchronize and its github name

.. image:: /github_connector/static/description/sync_organization.png

Optionaly, once organization created, you have to create series of your project

* Go to 'Github' / 'Organizations' / click on your organization /
  'Organization Series' Tabs

.. image:: /github_connector/static/description/organization_series.png

For each branches of your repositories, you can download the Source Code, and
once downloaded you can analyze it. Analyze in this module is basic. (For the
time being, it just gives branches sizes). But you can develop an extra Odoo
Custom module to extend analyze function and get extra stats, depending of your
needs.

.. image:: /github_connector/static/description/repository_branch_list.png

Reporting
=========

This module provides several reportings.

**Commits by branches and by series**

.. image:: /github_connector/static/description/reporting_commit_by_repository_and_serie.png

**Branches by Series**

.. image:: /github_connector/static/description/reporting_branches_by_serie.png

**Sizes by Series**

.. image:: /github_connector/static/description/reporting_sizes_by_serie.png

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Sébastien BEAU (sebastien.beau@akretion.com)
* Benoît GUILLOT (benoit.guillot@akretion.com)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
