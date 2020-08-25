from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from backup.models import Campaign, BackupEntry


class TestViews(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser1'
        self.password = 'testpass8675309'
        self.user = User.objects.create(
            username=self.username,
            is_active=True,
        )
        self.user.set_password(self.password)
        self.user.save()
        self.client = Client()

        Campaign.objects.create(
            title="Test Campaign 1",
            slug="test-camp-1",
            active=True,
            backup_daily=False,
            condense_weekly=False,
            condense_monthly=False,
            condense_yearly=False
        )

    def test_index_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'index.html')
        self.assertEqual(len(response.context['campaigns']), 1)

    def test_index_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('index'), {'title': 'Test Camp 2', 'slug': 'test-camp-2'})
        self.assertEqual(response['location'], '/campaign/2')
        self.assertEqual(Campaign.objects.count(), 2)
        self.assertEqual(Campaign.objects.last().title, 'Test Camp 2')

    def test_campaign_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('campaign', kwargs={'camp_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'campaign.html')
        self.assertEqual(response.context['campaign'].id, 1)

    def test_campaign_post(self):
        self.client.force_login(self.user)
        form_data = {'title': 'Test Camp 3', 'slug': 'test-camp-3'}
        response = self.client.post(reverse('campaign', kwargs={'camp_id': 1}), form_data)
        self.assertEqual(response['location'], '/campaign/1')
        self.assertEqual(Campaign.objects.last().title, 'Test Camp 3')
