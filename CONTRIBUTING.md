# Contribute to the OCA's Odoo instance

This guide aims to help happy volunteers to contribute to the OCA's Odoo instance. I
suppose mainly the OCA's Internal Tools team.

It's split into 3 sections:

- [Concepts](#concepts): Main concepts to understand and general organization
- [Processes](#processes): Helping doing the work without missing crucial steps
- [HowTos](#howto): How to do specific tasks

## Concepts

This repository is setup as other OCA's repositories to launch CI as usual and as an
extra configuration in order to build the OCA' Docker image used by our Odoo instance,
as well as facilitate the bootstrapping of a development environment.

Managing and freezing modules versions rely on python tools:

- [uv](https://docs.astral.sh/uv/)
- [hatch-odoo](https://pypi.org/project/hatch-odoo/)

## Processes

Here we focus on what to do without explaining how to do it.

### Release

While we are building and publishing a docker image the current state is that the image
is build at deploy time on OCA server.

While technically speaking there is nothing more than accessing to a public commit to
deploy a new version it's a common practice to merge your work on branch 14.0 before
deploying a new version in production.

> **Note**: in this repository we allow unreleased dependencies.

### deployment

Ask administrator to deploy the given commit.

## HowTos

Here we focus on how to do it, it's a suggest way to works but feel free to use your own
way.

### Setup developer environment

Requirements:

- Postgresql
- [uv](https://docs.astral.sh/uv/)
- Some dependencies to be able to build some python packages: `libpq-dev`,
  `build-essential`, TODO
- wkhtmltopdf

Prepare a python virtual environment with the correct python version (which uv will
download for you if necessary) and install the required dependencies:

```bash
uv sync
```

### Neutralize database

If you are allow to access to a production database, neutralization happens while
stating the Docker container if the running environnement is not the production server.

On development, if your are not using docker you can running neutralize scripts such as:

```bash
 find entrypoints/neutralize/*.sql -type f -exec  psql <dbname> -f {} \;
```

### Development

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

### use unreleased dependency

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

### Setup database and launch tests

- setup database with demo data and all oca modules installed

```bash
uv run odoo -d oca-custom -i oca_all --stop-after-init --without-demo=
```

- run tests using pytest launcher

```bash
uv run pytest --odoo-database oca-custom --cov ./oca_psc_team/ oca_psc_team/
```

### Update OCB Branch

```bash
uv sync -P odoo
```

### Update a specific OCA module dependency using the latest pypi release

```bash
uv sync -P odoo14-addon-<module-name>
```

### Bump all dependencies to the latest version

```bash
uv sync -U
```
