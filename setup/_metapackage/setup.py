import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-oca-custom",
    description="Meta package for oca-oca-custom Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-oca_custom',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
