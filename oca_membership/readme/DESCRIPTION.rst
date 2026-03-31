
This module adds several independant features.

- **Target role [TO FINISH: logique de facturation]**
  New field *Target role* on Members form: it defines the role the
  member will receive when paying for its *next* membership. It should
  be updated by the association' secretary when members roles change,
  like on election, before the memberships are renewed.

- **Working Group**
  New menu "Working Group" in *Membership* app. They are native Odoo objects
  *Mail Groups* `mail.group` with custom boolean *Is a Working Group* enabled.
  When creating a *Mail Group*, create a *Partner Tag* with the same name. Then,
  to add Members to a *Mail Group*, add the same tag to them.
