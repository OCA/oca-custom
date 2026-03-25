
PSC synchronisation
-------------------

In order to display accurate PSC information on the website, this module rely on the module `vpc/vpc_github`.
To keep models `vcp.oca.psc` and `oca.psc.member` updated, one should ensure in the the Virtual Control Platform app that:

- there is a *Platform* named *"OCA"* (the name matters)
- a Github *Personal access token* is configured in the tab *API Keys*. **This step is manual and cannot be automatized**
- the repository "*repo-maintainer-conf*" is scheduled as *Scheduled Branch Update*
- on the branch "*master*" of this repo, the *Processing rules* named *Update PSC list & members (OCA)* is configured

Those configuration comes at this module installation, except for the platform's *API Key*.
