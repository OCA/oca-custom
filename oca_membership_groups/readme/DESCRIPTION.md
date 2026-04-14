This module manages the mailing lists inside the OCA. It relies on the
native Odoo model *Mailing Group* mail.group.

## Main features

This module allows:

- to distinguish Working Groups from other Mail Groups, so they are
  published on the website on members' page
- to keep up-to-date the Mail Groups compared to Members roles in the
  association (like *Members* and *Delegate* mailing list)
- removes the expired members **with a grace period**
- retain the wish of the members who unsubscribed, to prevent spamming
  them by re-adding them to the mailing lists

## Notes

- Any Mailing Group member, being a portal or internal Odoo users, may
  subscribe or unsubscribed from */groups* controller
- The *Board Members* mailing list is managed manually (not automatized)
- The *Contributor* mailing list too, and is public
