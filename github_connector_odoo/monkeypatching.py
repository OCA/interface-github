# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.release as release
from odoo.modules import module

adapt_version_original = module.adapt_version


def adapt_version(version):
    """Overwrite the method to avoid the error if use values that do not contain serie
    (17.0), for example 4.0
    """
    serie = release.major_version
    if version == serie or not version.startswith(serie + "."):
        return f"{serie}.{version}"  # Similar to 16.0
    return adapt_version_original(version)


# Monkey-patching of the method
module.adapt_version = adapt_version
