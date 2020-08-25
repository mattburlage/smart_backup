# smart_backup

Smart Backup is a simple Django project to help automatically back up PostgreSQL databases periodically and keep the storage footprint to a minumum by selectively removing backups once a certain time period has elapsed.

For example, with every setting on:

- A backup would be taken daily.
- Every sunday, all backups from 7 days+ will be removed except for one per week.
- Every 1st of the month, all backups from 31 days+ will be removed except for one per month.
- Every 1st of the year, all backups from 366 days+ will be removed except for one per year.

