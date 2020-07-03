import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-oca-custom",
    description="Meta package for oca-oca-custom Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-oca_custom',
        'odoo13-addon-oca_psc_team',
        'odoo13-addon-project_members',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
