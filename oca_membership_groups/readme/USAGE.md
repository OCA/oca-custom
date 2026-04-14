## Set up synchronization between Mail Groups and Member Categories

On Member's form:

- On Member Categories change, the Mail Groups are updated
- To view it: open the *Mail Groups* smart button
- If needed, filter with *Unsubscribed (archived)* or *In grace period*

## Disable a grace period

If a member is in a Grace Period but you want to keep he/her on a Mail
Group:

- Browse to "Members / Groups" and click on the "Members" smart button
- Filter on *In grace period*
- Manually set *Grace date end* to a far date in the future. It will not
  be overriden by the automated mechanism.

## Send Email Marketting (Mass Mailing) based on Member Categories

- Browse to "Email Marketing / \[+ New\]"
- Recipients: select "Contact"
- In the *Mail Body*, replace the *Unsubscribe* link with this one:
  <https://odoo-community.org/groups>

A default domain helps filtering on all active members. You may save
this domain as favorite filter, and / or modify it.
