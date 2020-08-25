from backup.models import BackupEntry


def total_size():
    backups = BackupEntry.objects.all()

    size = 0
    for backup in backups:
        size += backup.file.size

    return size
