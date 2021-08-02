import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-oca-custom",
    description="Meta package for oca-oca-custom Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-oca_custom',
        'odoo14-addon-oca_event_badge',
        'odoo14-addon-oca_psc_team',
        'odoo14-addon-project_members',
        'odoo14-addon-website_oca_psc_team',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
