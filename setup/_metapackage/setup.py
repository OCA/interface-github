import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-interface-github",
    description="Meta package for oca-interface-github Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-github_connector',
        'odoo11-addon-github_connector_odoo',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
