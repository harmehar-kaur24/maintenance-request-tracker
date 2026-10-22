from io import StringIO

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from tracker.forms import RequestForm
from tracker.models import Request


def run_command(name, *args):
    """Run a management command and return what it printed."""
    output = StringIO()
    call_command(name, *args, stdout=output)
    return output.getvalue()


class SeedRequestCountSettingTests(TestCase):
    def test_setting_exists(self):
        self.assertTrue(hasattr(settings, 'SEED_REQUEST_COUNT'))

    def test_setting_is_a_positive_whole_number(self):
        self.assertIsInstance(settings.SEED_REQUEST_COUNT, int)
        self.assertGreater(settings.SEED_REQUEST_COUNT, 0)


class SeedCommandTests(TestCase):
    def test_creates_default_number_of_requests(self):
        output = run_command('seed')
        self.assertEqual(Request.objects.count(), settings.SEED_REQUEST_COUNT)
        self.assertIn(f'Created {settings.SEED_REQUEST_COUNT} requests.', output)

    @override_settings(SEED_REQUEST_COUNT=7)
    def test_default_comes_from_setting(self):
        run_command('seed')
        self.assertEqual(Request.objects.count(), 7)

    def test_count_option_sets_number_of_requests(self):
        output = run_command('seed', '--count', '15')
        self.assertEqual(Request.objects.count(), 15)
        self.assertIn('Created 15 requests.', output)

    def test_count_of_zero_creates_nothing(self):
        run_command('seed', '--count', '0')
        self.assertEqual(Request.objects.count(), 0)

    def test_negative_count_is_rejected(self):
        with self.assertRaisesMessage(CommandError, '--count cannot be negative.'):
            run_command('seed', '--count', '-5')
        self.assertEqual(Request.objects.count(), 0)

    def test_non_numeric_count_is_rejected(self):
        with self.assertRaises(CommandError):
            run_command('seed', '--count', 'abc')
        self.assertEqual(Request.objects.count(), 0)

    def test_adds_to_existing_requests(self):
        Request.objects.create(title='Existing request')
        run_command('seed', '--count', '10')
        self.assertEqual(Request.objects.count(), 11)
        self.assertTrue(Request.objects.filter(title='Existing request').exists())

    def test_seeded_requests_are_valid(self):
        run_command('seed', '--count', '50')
        for service_request in Request.objects.all():
            form = RequestForm(data={'title': service_request.title, 'description': service_request.description, 'urgency': service_request.urgency})
            self.assertTrue(form.is_valid(), form.errors)
            self.assertNotEqual(service_request.description, '')


class UnseedCommandTests(TestCase):
    def test_removes_seeded_requests(self):
        run_command('seed', '--count', '25')
        output = run_command('unseed')
        self.assertEqual(Request.objects.count(), 0)
        self.assertIn('Deleted 25 requests.', output)

    def test_removes_requests_that_were_not_seeded(self):
        Request.objects.create(title='Created by hand')
        run_command('unseed')
        self.assertEqual(Request.objects.count(), 0)

    def test_runs_on_empty_database(self):
        output = run_command('unseed')
        self.assertEqual(Request.objects.count(), 0)
        self.assertIn('Deleted 0 requests.', output)

    def test_seed_works_again_after_unseed(self):
        run_command('seed', '--count', '5')
        run_command('unseed')
        run_command('seed', '--count', '5')
        self.assertEqual(Request.objects.count(), 5)