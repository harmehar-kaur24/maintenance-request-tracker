from django.test import TestCase

from tracker.forms import RequestForm


class RequestFormTests(TestCase):
    def test_valid_with_title_and_description(self):
        form = RequestForm(data={'title': 'Leaking tap', 'description': 'Kitchen sink', 'urgency': 1})
        self.assertTrue(form.is_valid())

    def test_valid_without_description(self):
        form = RequestForm(data={'title': 'Leaking tap', 'description': '', 'urgency': 1})
        self.assertTrue(form.is_valid())

    def test_title_is_required(self):
        form = RequestForm(data={'title': '', 'description': 'Kitchen sink'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_cannot_be_longer_than_200_characters(self):
        form = RequestForm(data={'title': 'x' * 201})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_save_creates_request(self):
        form = RequestForm(data={'title': 'Leaking tap', 'description': 'Kitchen sink', 'urgency': 1})
        service_request = form.save()
        self.assertEqual(service_request.title, 'Leaking tap')
        self.assertIsNotNone(service_request.pk)

    def test_inputs_have_bootstrap_class(self):
        form = RequestForm()
        self.assertIn('class="form-control"', str(form['title']))
        self.assertIn('class="form-control"', str(form['description']))
        self.assertIn('class="form-select"', str(form['urgency']))