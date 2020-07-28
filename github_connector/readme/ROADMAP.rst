* For the time being, Github API doesn't provide some informations that are
  available by the classic UI, that includes:

  1. team hierarchy: the field is present in the model github_team.parent_id,
     but unused.

* Possible improvements:

  1. Create a new module github_connector_website, that could display
     teams / repositories / branches informations for non logged users.

  2. Analyze commits (author, quantity by series, etc...):
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
