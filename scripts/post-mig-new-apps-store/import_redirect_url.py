#!/usr/bin/env python3

import csv

import click
import click_odoo

# This script should be removed after going in production
# It's should be executed manually after importing all the data
# from github, the list of url come from an extraction of apps.odoo-community.org


@click.command()
@click_odoo.env_options(default_log_level="error")
@click.option("--csv", "csv_path", required=True, type=click.Path(exists=True))
def main(env, csv_path):
    lang_id = env.ref("base.lang_en").id
    created = skipped = missing = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            module = env["vcp.odoo.module"].search(
                [("name", "=", row["technical_name"])], limit=1
            )
            if not module:
                click.echo(click.style(f"MISSING {row['technical_name']}", fg="red"))
                missing += 1
                continue

            if env["url.url"].search([("key", "=", row["website_url"])], limit=1):
                skipped += 1
                continue

            env["url.url"].create(
                {
                    "key": row["website_url"],
                    "res_model": "vcp.odoo.module",
                    "res_id": module.id,
                    "redirect": True,
                    "lang_id": lang_id,
                }
            )
            click.echo(click.style(f"OK      {module.name}", fg="green"))
            created += 1

    click.echo(f"\ncreated={created} skipped={skipped}")


if __name__ == "__main__":
    main()
