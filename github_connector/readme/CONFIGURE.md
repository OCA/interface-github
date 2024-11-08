Once installed, you have to:

1.  Open your odoo.conf file and add extra settings to mention Github
    credentials, and the local path where the source code will be
    downloaded:
    - `source_code_local_path = /workspace/source_code/`

Note: you can define the route as environment variable using the key
SOURCE_CODE_LOCAL_PATH

Note: make sure that Odoo process has read / write access on that folder

> - `github_token = your_github_access_token`

Note: The login/password auth has been deprecated by GitHub.
<https://docs.github.com/en/rest/overview/other-authentication-methods#via-username-and-password>

1.  Go to 'Settings' / 'Technical' / 'Parameters' / 'System Parameters'
    and define the following values:

    1.  `github.max_try`: number of call to the API before an error is
        raised. The more unstable/slow your connection, the higher
        should be this value
    2.  `git.partial_commit_during_analysis`: Set to `True` if you want
        to commit the result of the analysis in the database after each
        repository analysis. We recommend to set to `True` when you
        perform the initial download (potentially with a lot of
        repositories) in order to reduce the size of the transaction

    ![image](../static/description/github_settings.png)

2.  Go to your(s) user(s) form to add them in the new 'Connector Github
    Manager' groups. The members of this group will have the possibility
    to run Github synchronization.

## Technical Information

This module provides 4 crons that you can enable:

- Synchronize All Organizations and Teams (`cron_update_organization`)
- Synchronize Branches List for All repositories
  (`cron_update_branch_list`)
- Download Source Code for All Github Branches (`cron_download_code`)
- Analyze Source Code for All Github Branches (`cron_analyze_code`)
