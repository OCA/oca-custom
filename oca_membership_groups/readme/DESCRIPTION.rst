
This module manages the mailing lists inside the OCA.
It relies on the native Odoo model *Mailing Group* `mail.group`.
There are 3 kinds of groups (=mailing lists):

1. **Groups related to the membership process**
   Example: like *Members*, *Contributors* and *Delegate*.
   Note: the *Board Members* mailing list *is* related to the membership process
   but it managed manually, like the 3rd type *Others*.
   
   * Website: displayed but via the *Roles*.
   * Provisioning of the members in the mailing list: automated from the *Active roles*.
   * Configuration: on *Members / Configuration / Membership Categories*, choose the
    Mailing Groups that must be inherited by the members of a *Membership Category*.

2. **Working Groups: they are displayed on the member's website page**
   * Website: displayed
   * Provisioning: to manage manually, for instance by the association secretary.
     Path: browse a member form, go to *Membership* tab, and use the field *Mail Groups*.
   * Configuration: browse to *Members / Groups*, and set the boolean *Is a Working Group*.

3. **Others: standard Mailing Group, like regional groups**
   * Website: they are not displayed.
   * Provisioning: like for Working Groups, it is manual from the Member form.


Hypothesis:
* The provisioning of contact to Mailing Group does not rely on Tags, leaving them for all other purposes.
* Except for grace period, the members of Mailing Groups is managed by logics in module code and not by CRON.
* A member who has unsunbscribed **must not** be added again into the same group (especially for
  type *1 - Groups related to the membership process*).
