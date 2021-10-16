import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-oca-custom",
    description="Meta package for oca-oca-custom Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-oca_custom',
        'odoo12-addon-oca_event_badge',
        'odoo12-addon-oca_psc_team',
        'odoo12-addon-project_members',
        'odoo12-addon-website_oca_integrator',
        'odoo12-addon-website_oca_psc_team',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
