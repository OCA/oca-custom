.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

======================================
Load Github Data in your Odoo Instance
======================================

This module allow you to

* recover social informations from Github. (Members of an organizations,
  Pull requests, Issues, Comments, ...)
* download source code

Installation
============

Nothing special is needed to install this module.

Configuration
=============

Once installed, you have to:

* go to 'Settings' / 'Technical' / 'Parameters' / 'System Parameters'
* set credentials to access to github
* set a local folder, if you want to download code source from github

.. image:: /github_connector/static/description/github_settings.png


Usage
=====

To recover information from github, you have to:

* go to 'Github' / 'Settings' / 'Sync Object'
* Select the object type you want to synchronize and its github name

.. image:: /github_connector/static/description/sync_organization.png


Optionaly, once organization created, you have to create series of your project

* Go to 'Github' / 'Organizations' / click on your organization /
  'Organization Series' Tabs

.. image:: /github_connector/static/description/organization_series.png

For each branches of your repositories, you can download the Source Code, and
once downloaded you can analyze it. Analyze in this module is basic. (For the
time being, it just gives branches sizes). But you can develop an extra Odoo
Custom module to extend analyze function and get extra stats, depending of your
needs.

.. image:: /github_connector/static/description/repository_branch_list.png

Reporting
=========

This module provides several reportings.

**Branches by Series**

.. image:: /github_connector/static/description/reporting_branches_by_serie.png

**Sizes by Series**

.. image:: /github_connector/static/description/reporting_sizes_by_serie.png


Known issues / Roadmap
======================


Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Sébastien BEAU (sebastien.beau@akretion.com)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
