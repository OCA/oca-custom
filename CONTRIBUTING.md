# Contribute to the OCA's Odoo instance (kick-starter guide)

This one-pager guide aims to help happy volunteers to contribute to the OCA's Odoo
instance, supposedly the OCA's Internal Tools team.

## Table of content

1. [Introduction](#introduction): who we are, how we work
2. [Getting Started](#getting-started)
   - [Concepts](#concepts): main concepts to understand and general organization
   - [Processes](#processes): helping doing the work without missing crucial steps
   - [How-Tos](#how-tos): how to do specific tasks
3. [FAQ](#FAQ)

## Introduction

This repository is managed by OCA's Internal Tools team:

- email: [internaltools@odoo-community.org](mailto:internaltools@odoo-community.org)
- [Github team page](https://github.com/orgs/OCA/teams/internal-tools)
- [Github project Kanban](https://github.com/orgs/OCA/projects/13)

Please refer to the document
[Scope & Objective](https://docs.google.com/document/d/1RcOUstPJDev1bgPZcNXWiHBt5PeqraisU5bKIZatcnY/edit?pli=1&tab=t.0#heading=h.jrsgv4k2u2ao)
to understand the governance and missions of the Internal Tools team within the OCA.
Under the watch of OCA board, this document mainly explains:

- The "Raison d'être" of the Internal Tools group
- Tasks and responsabilities
- Autonomy scope
- How to become part of the group
- Internal governances (leaders & members)
- Useful processes to start working in the group

## Getting Started

This section will guide you to:

1. Build a test environment on a developer's machine, replicating OCA's Odoo production
   instance
2. Push a change in production to OCA's Odoo production instance

### Concepts

This repository is setup as other OCA's repositories to launch CI as usual and as an
extra configuration in order to build the OCA' Docker image used by our Odoo instance,
as well as facilitate the bootstrapping of a development environment.

Managing and freezing modules versions rely on python tools:

- [uv](https://docs.astral.sh/uv/)
- [hatch-odoo](https://pypi.org/project/hatch-odoo/)

### Processes

Here we focus on what to do without explaining how to do it.

### Release

While we are building and publishing a docker image the current state is that the image
is build at deploy time on OCA server.

While technically speaking there is nothing more than accessing to a public commit to
deploy a new version it's a common practice to merge your work on branch 14.0 before
deploying a new version in production.

> **Note**: in this repository we allow unreleased dependencies.

#### Deployment

Ask administrator to deploy the given commit.

### How-Tos

Here we focus on how to do it, it's a suggest way to works but feel free to use your own
way.

#### Setup developer environment

Requirements:

- **uv**: several methods exist to install it, one can be
  `curl -LsSf https://astral.sh/uv/install.sh | sh`. It will install other
  prerequisites.
- Postgresql
- Some dependencies to be able to build some python packages: `libpq-dev`,
  `build-essential`, ...
- wkhtmltopdf

Run the following commands to prepare a python virtual environment with the correct
python version (which uv will download for you if necessary) and install the required
dependencies:

```bash
git clone git@github.com:OCA/oca-custom -branch 14.0
cd oca-custom
uv sync
```

#### Setup database

Setup database with demo data and all OCA modules installed:

```bash
uv run odoo -d oca-custom -i oca_all --stop-after-init --without-demo=
```

The `oca_all` module contains the `__manifest__.py` with all Odoo modules dependencies
for the OCA Odoo instance.

#### Neutralize database

If you are allow to access to a production database, neutralization happens while
stating the Docker container if the running environnement is not the production server.

On development, if your are not using docker you can running neutralize scripts such as:

```bash
 find entrypoints/neutralize/*.sql -type f -exec  psql <dbname> -f {} \;
```

#### Development

For addons living in this repository, you can just change code and restart Odoo with the
`uv run` command.

For addons in other repositories, the procedure is as follows:

- check out the repository somewhere, ie /src/\$repo
- add the following line to `pyproject.toml` in the `[tool.uv.sources]` section:

  ```pyproject
  odoo14-addon-$youraddon = { path = "/srv/$repo/setup/$youraddon", editable = true }
  ```

- run `uv sync`
- restart Odoo

#### Use unreleased dependency

There is two different goals:

- making the test CI pass: using regular test-requirements.txt files add a line such as

  ```
  odoo14-addon-membership-delegated-partner-line @ git+https://github.com/OCA/vertical-association@refs/pull/151/head#subdirectory=setup/membership_delegated_partner_line
  ```

- bring the unreleased dependency in the uv project (and the built docker image), add
  the following line to `pyproject.toml` in the `[tool.uv.sources]` section:

  ```pyproject
  odoo14-addon-membership-delegated-partner-line = { git = "https://github.com/OCA/vertical-association", rev = "refs/pull/151/head", subdirectory = "setup/membership_delegated_partner_line" }
  ```

#### Launch tests

Run tests using pytest launcher.

```bash
uv run pytest --odoo-database oca-custom --cov ./oca_psc_team/ oca_psc_team/
```

#### Update OCB Branch

```bash
uv sync -P odoo
```

#### Update a specific OCA module dependency using the latest pypi release

```bash
uv sync -P odoo14-addon-<module-name>
```

Note bug https://github.com/astral-sh/uv/issues/14684, that says if multiple packages
are sourced from the same branch/PR, we need to specify both of them as to upgrade,
otherwise they don't get rescanned.

#### Bump all dependencies to the latest version

```bash
uv sync -U
```

## FAQ

#### How can I start contributing in OCA toolings?

- Get to know the manifest document of OCA's Internal Tools team:
  [Scope & Objective](https://docs.google.com/document/d/1RcOUstPJDev1bgPZcNXWiHBt5PeqraisU5bKIZatcnY/edit?pli=1&tab=t.0#heading=h.jrsgv4k2u2ao).
- Write to us at
  [internaltools@odoo-community.org](mailto:internaltools@odoo-community.org).
- Install a test environment on your machine of the OCA's Odoo instance by following the
  [§ Getting Started](#getting-started).

#### How to communicate with the OCA Internal Tools?

Our main communication channel is the mailing list
[internaltools@odoo-community.org](mailto:internaltools@odoo-community.org). For
task-related discussion, also directly use the Chatter of the Odoo tasks.

#### Where is the tasks backlog of the OCA Internal Tools?

We use the Odoo project **OCA internal tools workgroup** on the OCA's Odoo instance to
organize our tasks and priorities. A public access to the project can be provided to OCA
members who contributes to the tooling tasks (not requesting privacy form signing).

#### How to access the backend of OCA's Odoo instance?

It can be useful to access Odoo back-end for both task management and browse instance's
modules and data. For such, prerquisites are:

- being a member of the OCA and the **OCA Internal Tools group**
- be registered on OCA's Odoo instance
- fullfil and send back the **Data protection & privacy** form, available on OCA website
  [Resources / How to guides / Protect data & privacy when you support OCA projects](https://odoo-community.org/privacy)

#### What are useful Github repositories?

- The current **oca-custom** is the main repository. It contains both all Odoo modules
  dependencies of OCA instance in `oca_all/__manifest__.py` and all configuration to
  build an Odoo test instance the `uv`, as described in
  [Getting Started](#getting-started).
- [**apps-store**](https://github.com/OCA/apps-store/tree/14.0) holds mechanisms of OCA
  modules replication to official Odoo's App Store

#### How to get representive data, for troubleshooting and test?

Contact the mailing list to get a neutralized and anonymized database.

#### How to gain command line access and read logs?

Only a few people have admin server access, please reach the mailing list for further
details.

#### How to refresh test instance from production instances (on the server)?

`home/odoo/instance/README` gives some guidance.
