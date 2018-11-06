import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-oca-custom",
    description="Meta package for oca-oca-custom Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-oca_custom',
        'odoo11-addon-oca_event_badge',
        'odoo11-addon-project_members',
        'odoo11-addon-website_oca_integrator',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
