Once installed, you have to:

#. Open your odoo.conf file and add extra settings to mention Github
   credentials, and the local path where the source code will be downloaded:

   * ``source_code_local_path = /workspace/source_code/``

Note: make sure that Odoo process has read / write access on that folder

   * ``github_login = your_github_login``
   * ``github_password = your_github_password``

#. Go to 'Settings' / 'Technical' / 'Parameters' / 'System Parameters'
   and define the following values:

   #. ``github.max_try``: number of call to the API before an error
      is raised. The more unstable/slow your connection, the higher should be
      this value
   #. ``git.partial_commit_during_analysis``: Set to ``True`` if you want to
      commit the result of the analysis in the database after each repository
      analysis. We recommend to set to ``True`` when you perform the initial
      download (potentially with a lot of repositories) in order to reduce the
      size of the transaction

   .. image:: ../static/description/github_settings.png

#. Go to your(s) user(s) form to add them in the new 'Connector Github Manager'
   groups. The members of this group will have the possibility to run Github
   synchronization.
