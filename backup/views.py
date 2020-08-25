from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from backup.forms import CampaignForm
from backup.models import Campaign, BackupEntry
from backup.tasks import backup_postgres
from backup.utils import total_size


@login_required
def index(request):
    if request.method == 'GET':
        context = {
            'campaigns': Campaign.objects.all(),
            'new_form': CampaignForm(),
            'total_size': total_size(),
        }
        return render(request, 'index.html', context=context)
    else:
        form = CampaignForm(request.POST)

        if form.is_valid():
            new_item = form.save()
        else:
            return redirect('index')

        return redirect('campaign', camp_id=new_item.pk)


@login_required
def campaign(request, camp_id):
    if request.method == 'GET':
        camp = Campaign.objects.get(pk=camp_id)

        context = {
            'campaign': camp,
            'camp_form': CampaignForm(instance=camp),
        }
        return render(request, 'campaign.html', context=context)
    else:
        camp = Campaign.objects.get(pk=camp_id)

        form = CampaignForm(request.POST, instance=camp)

        if form.is_valid():
            form.save()

        return redirect('campaign', camp_id=camp_id)


def initiate(request, camp_id):
    backup_postgres(camp_id, source='Manual')

    return redirect('campaign', camp_id=camp_id)


def keep_safe_toggle(request, bac_id):
    backup = BackupEntry.objects.get(pk=bac_id)
    backup.do_not_delete = not backup.do_not_delete

    return redirect('campaign', camp_id=backup.campaign_id)
