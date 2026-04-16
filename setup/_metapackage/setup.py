import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-interface-git",
    description="Meta package for oca-interface-git Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-github_connector>=16.0dev,<16.1dev',
        'odoo-addon-github_connector_odoo>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
