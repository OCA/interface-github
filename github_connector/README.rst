.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

======================================
Load Github Data in your Odoo Instance
======================================

This module allow you to

* Recover social informations from Github. (Organizations, Teams, Users)
* Recover Code structure informations from Github (Repositories, Branches)
* Download source code from Github

Configuration
=============

Once installed, you have to:

* Open your openerp.cfg file and add extra settings to mention github
  credentials, and the local path where the source code will be downloaded

``github_login = your_github_login``

``github_password = your_github_password``

``source_code_local_path = /workspace/source_code/``

Note: make sure that Odoo process has read / write access on that folder

* go to 'Settings' / 'Technical' / 'Parameters' / 'System Parameters'
  and define the following values:

1. ``github.max_try``: mention the number of calls to the API, before an error
   is raised. Set an high value if your connection is bad
2. ``git.partial_commit_during_analyze``: Set to True if you want to commit
   in the database the result of the analysis after each repository analysis.
   (If you have a lot of repositories to reduce the size of the transaction,
   when you realize the first big analyse.)

.. image:: /github_connector/static/description/github_settings.png

* Go to your(s) user(s) form to put them in the new 'Connector Github Manager'
  groups. The members of this group will have the possibility to run Github
  synchronization.

Usage
=====

Load from Github
----------------

To recover information from github, you have to:

* go to 'Github' / 'Settings' / 'Sync Object'
*  Select the object type you want to synchronize and its github name

.. image:: /github_connector/static/description/sync_organization.png

* Once done for your organization(s), go to 'Github' / 'Github Commnunity' /
  'Organizations'

.. image:: /github_connector/static/description/github_organization_kanban.png

* Optionaly, once organization created, you can create milestones of your
  projects. Go to 'Github' / 'Organizations' / click on your organization /
  'Organization Milestones' Tabs

.. image:: /github_connector/static/description/github_organization_milestones.png

This setting will prevent to download undesired branches, downloading only
main branches (releases).

* In the 'Settings' tab, set repositories you don't want to download
  (or repositories you want to download). If 'Specific repositories' is set,
  'Ignored Repositories' value is ignored.

* In the 'Settings' tab, set the URL of the 'External Services' you use
  for Continuous Integration and Coverage.

.. image:: /github_connector/static/description/github_organization_external_services.png

* Once done, click on buttons 'Syncs', to synchronize repositories, teams and
  members. (This process can take a while depending of your size)

.. image:: /github_connector/static/description/github_organization_sync_buttons.png

* You can synchronize members teams. Go to 'Teams' / tree view / 'Actions'
  'Update from Github'.

.. image:: /github_connector/static/description/github_team_kanban.png

In each team, you can see the members list and the role of the members

.. image:: /github_connector/static/description/github_team_partner_kanban.png

In each team, you can see the repositories list but not the permissions of the
team. (See 'Known I'ssues Section)

.. image:: /github_connector/static/description/github_team_repository_kanban.png

* You can synchronize the branches of your repositories. Go to 'Repositories' /
  tree view / 'Actions' / 'Update from Github'

.. image:: /github_connector/static/description/github_repository_kanban.png

In each repository, you can see the main branches list and the size of code
source.

.. image:: /github_connector/static/description/github_repository_branch_kanban.png

* Finally, you can download locally the source code of all your branches.
  Go to 'Repository Branches' / tree view / 'Actions'
  'Download and Analyse Source Code'.

.. image:: /github_connector/static/description/wizard_download_analyze.png

In the tree view you can update manually source code or refresh analysis.

.. image:: /github_connector/static/description/github_repository_branch_list.png


Create in Github
----------------

You have the possibility to creates two items in Github

1. Teams:
   Go to 'Settings' / 'Create Team in Github'. Set the information and click
   on Create in Github. odoo will try to create the team. If access right is OK,
   and datas are correct, the creation will be done in github and then, a
   synchronization will be done, to create the according team in the Odoo
   instance.

.. image:: /github_connector/static/description/wizard_create_team.png

2. Repositories:
   Go to 'Settings' / 'Create Team in Github'. Set the information and click
   on Create in Github.

.. image:: /github_connector/static/description/wizard_create_repository.png

Note
----
Analyze in this module is basic. (For the time being, it just gives branches
size). But you can develop an extra Odoo Custom module to extend analyze
function and get extra stats, depending of your needs.

In that way, you can see the module github_connector_odoo, if your repositories
contain Odoo modules.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/229/10.0

Reporting
=========

This module provides several reportings.

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

2. Analyse commits. (author, quantity by milestones, etc...)
   this feature has been partially implemented in a V8.0 PR.

3. Synchronize Pull Request, Issues, Comments.
   this feature has been partially implemented in a V8.0 PR.

* Refactor the github connector:

A python librairy is available named, PyGitHub. It could be interesting
to use it, instead of using custom code. However, this lib doesn't provides
good access to child object, that generates for the time being, unecessary
api calls. For exemple, updating a repository should call before a call to
the parent organization. (The current module is so faster)

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

To contribute to this module, please visit http://odoo-community.org.
