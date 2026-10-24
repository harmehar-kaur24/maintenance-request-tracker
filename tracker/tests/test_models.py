from django.test import TestCase

from tracker.models import Request


class RequestModelTests(TestCase):
    def test_create_request(self):
        service_request = Request.objects.create(title='Leaking tap', description='Kitchen sink')
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(service_request.title, 'Leaking tap')
        self.assertEqual(service_request.description, 'Kitchen sink')
        self.assertEqual(service_request.urgency, 1)

    def test_description_is_optional(self):
        service_request = Request.objects.create(title='Broken chair')
        self.assertEqual(service_request.description, '')

    def test_str_returns_title(self):
        service_request = Request(title='Flickering lights')
        self.assertEqual(str(service_request), 'Flickering lights')

    def test_newest_requests_come_first(self):
        first = Request.objects.create(title='First')
        second = Request.objects.create(title='Second')
        self.assertEqual(list(Request.objects.all()), [second, first])

    def test_set_urgency(self):
        service_request = Request.objects.create(
            title='Broken chair',
            urgency=2
        )
        self.assertEqual(service_request.urgency, 2)