1.  On a standard partner, open the new *Sponsorship* tab.
2.  Create or choose a *Sponsor Level*.
3.  Grant the partner access to the portal, using the native wizard of
    the action *Grant portal access* (on partners form or list views)
4.  On the website portal, the sponsor may login **with the user related
    to the company**. This process will not work with users related to
    sub-contacts of the company. From the `/my/account` page, the sponsor
    may edit its information in autonomy.
5.  When a sponsor field changes, a review process is started: the sponsor
    new information are *not* immediatly available on the website. They
    must be reviewed from Odoo backend by a reviewer. A reviewer is a member
    of the Activity Group named *Sponsors Reviewers*, configurable at
    *Settings / Technical / Activity Teams*.
6.  Reviewers are notified of the sponsor to review by activities on those
    sponsors. All reviewers receive a notification. Moreover, the new
    *Members / Sponsors* page is ordered by Sponsor to review firs. An
    explicit ribbon *To review* appear on their Kanban cards.
7.  On the sponsor's partner form, you may use the action
    *Sponsor Version History* to easily view the difference with previous
    information. The tab *Sponsor* also provides all last information.
8.  Once done, press the *Review sponsor* button in the *Sponsorship*
    tab. It re-starts the sponsor information synchronization with the
    website, thus pushing the information online very soon (by default,
    ~10min). This button also un-notify the other reviewers but removing
    the review activity.
9.  If a *Review* must be refused, you may leave the sponsor in *To review*
    state and close the activity. Its data will be kept in *idle* state, not
    being sent to the website. You may also correct the sponsor information
    by yourself from Odoo backend and validate the *Review*.
