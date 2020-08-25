from django.http import JsonResponse

from backup.models import BackupEntry
from backup.tasks import schedule_backup


def initiate_backup(request, camp_id):
    schedule_backup(camp_id, source='Manual')

    return JsonResponse({'msg': 'scheduled'})


def keep_safe_toggle(request, bac_id=None):
    if not bac_id:
        return JsonResponse({'msg': 'no bac_id'}, status=400)

    backup = BackupEntry.objects.get(pk=bac_id)

    backup.do_not_delete = not backup.do_not_delete
    backup.save()

    return_data = {
        'msg': "Toggled",
        'do_not_delete': backup.do_not_delete,
    }

    return JsonResponse(return_data)
