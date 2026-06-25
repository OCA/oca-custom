This module replaces oca_custom in v18.0.

The partner *Tags* are not related anymore to any process related to
membership of mailing list:

- the almost-native *Membership Categories* informs about a member's
  role in the association (*Member*, *Delegate*, *Board member*)
- the Mailing Groups for *Members*, *Delegate*, *Board member* are kept
  up-to-date by this module's code (with no CRON except the daily one to
  manage grace period)
