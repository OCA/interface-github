.. figure:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Load Github Data in your Odoo Instance
======================================

This module allows you to:

* Fetch into Odoo social information from Github (Organizations, Teams, Users)
* Fetch into Odoo Code structure information from Github (Repositories, Branches)
* Download source code from Github

Configuration
=============

Once installed, you have to:

#. Open your odoo.conf file and add extra settings to mention Github
   credentials, and the local path where the source code will be downloaded:

   * ``github_login = your_github_login``
   * ``github_password = your_github_password``
   * ``source_code_local_path = /workspace/source_code/``

   Note: make sure that Odoo process has read / write access on that folder

#. go to 'Settings' / 'Technical' / 'Parameters' / 'System Parameters'
   and define the following values:

   #. ``github.max_try``: number of call to the API before an error
      is raised. The more unstable/slow tyour connection, the higher should be
      this value
   #. ``git.partial_commit_during_analysis``: Set to ``True`` if you want to
      commit the result of the analysis in the database after each repository
      analysis. We recommend to set to ``True`` when you perform the initial
      download (potentially with a lot of repositories) in order to reduce the
      size of the transaction

   .. image:: /github_connector/static/description/github_settings.png

#. Go to your(s) user(s) form to add them in the new 'Connector Github Manager'
   groups. The members of this group will have the possibility to run Github
   synchronization.

Usage
=====

Initial upload from Github
----------------------------

To fetch information from Github, you have to:

#. go to 'Github' / 'Settings' / 'Sync Object'
#. Select the object type you want to synchronize and its Gthub name

   .. image:: /github_connector/static/description/sync_organization.png

#. Once done for your organization(s), go to 'Github' / 'Github Commnunity' /
   'Organizations'

   .. image:: /github_connector/static/description/github_organization_kanban.png

#. Optionally, once organization is created, you can create milestones for your
   projects. Go to 'Github' / 'Organizations' / click on your organization /
   'Organization Milestones' Tabs

   .. image:: /github_connector/static/description/github_organization_milestones.png

Select branches to download
---------------------------
This setting will prevent to download undesired branches, downloading only
main branches (releases):

#. In the 'Settings' tab, set repositories you don't want to download
   (or repositories you want to download). If 'Specific repositories' is set,
   'Ignored Repositories' value is ignored.

#. In the 'Settings' tab, set the URL of the 'External Services' you use
   for Continuous Integration and Coverage.

   .. image:: /github_connector/static/description/github_organization_external_services.png

#. Once done, click on buttons 'Syncs', to synchronize repositories, teams and
   members. (This process can take a while depending of your size)

   .. image:: /github_connector/static/description/github_organization_sync_buttons.png

Team / members synchronization
------------------------------
You can synchronize members teams:

#. Go to 'Teams' / tree view / 'Actions' / 'Update from Github'.

   .. image:: /github_connector/static/description/github_team_kanban.png

#. In each team, you can see the members list and the role of the members

   .. image:: /github_connector/static/description/github_team_partner_kanban.png

#. In each team, you can see the repositories list but not the permissions of the
   team. (See 'Known Issues' Section)

   .. image:: /github_connector/static/description/github_team_repository_kanban.png

Repositories synchronization
----------------------------
You can synchronize the branches of your repositories:

#. Go to 'Repositories' /
   tree view / 'Actions' / 'Update from Github'

   .. image:: /github_connector/static/description/github_repository_kanban.png

#. In each repository, you can see the main branches list and the size of code
   source.

   .. image:: /github_connector/static/description/github_repository_branch_kanban.png

Fetching the source code
------------------------
Finally, you can download locally the source code of all your branches:

#. Go to 'Repository Branches' / tree view / 'Actions' / 'Download and Analyse Source Code'.

   .. image:: /github_connector/static/description/wizard_download_analyze.png

#. In the tree view you can update manually source code or refresh analysis.

   .. image:: /github_connector/static/description/github_repository_branch_list.png

Data creation in Github
-----------------------

You have the possibility to creates two items in Github directly from Odoo

#. Teams:

   #. Go to 'Settings' / 'Create Team in Github'.
   #. Set the information and click on Create in Github.
   #. Odoo will try to create the team. If access right and datas are correct,
      the creation will be done directly in Github
   #. Later on, a synchronization will be performed, to create the according
      team in the Odoo instance.

   .. image:: /github_connector/static/description/wizard_create_team.png

#. Repositories:

   #. Go to 'Settings' / 'Create Team in Github'.
   #. Set the information and click on Create in Github.

   .. image:: /github_connector/static/description/wizard_create_repository.png

Note
----
Analysis in this module is basic: for the time being, it just gives branches
size.

Nevertheless, you can develop an extra Odoo Custom module to extend analysis
function and get extra statistics, depending on your needs.

In that way, you can see the module github_connector_odoo, if your repositories
contain Odoo modules.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/229/10.0

Reporting
=========

This module provides several reports

**Branches by Milestone**

.. image:: /github_connector/static/description/reporting_branches_by_milestone.png

**Sizes by Milestone**

.. image:: /github_connector/static/description/reporting_sizes_by_milestone.png

Technical Information
=====================

This module provides 4 crons that you can enable:

* Synchronize All Organizations and Teams (``cron_update_organization``)
* Synchronize Branches List for All repositories (``cron_update_branch_list``)
* Download Source Code for All Github Branches (``cron_download_code``)
* Analyze Source Code for All Github Branches (``cron_analyze_code``)

Roadmap / Known Issues
======================

* For the time being, Github API doesn't provide some informations that are
  available by the classic UI, that includes:

  1. team hierarchy: the field is present in the model github_team.parent_id,
     but unused.

* Possible improvements:

1. Create a new module github_connector_website, that could display
   teams / repositories / branches informations for non logged users.

2. Analyze commits (author, quantity by milestones, etc...):
   this feature has been partially implemented in a V8.0 PR.

3. Synchronize Pull Request, Issues, Comments: 
   this feature has been partially implemented in a V8.0 PR.

* Refactor the github connector:

  A python library called PyGitHub is available. It could be interesting
  to use it, instead of using custom code. However, this lib doesn't provide
  good access to child object, generating for the time being, unnecessary
  API calls. For example, updating a repository should call before a call to
  the parent organization (The current module is so faster).

.. code-block:: bash

   ``sudo pip install PyGitHub``

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

To contribute to this module, please visit https://odoo-community.org.
