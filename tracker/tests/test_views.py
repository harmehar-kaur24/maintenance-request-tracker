from django.test import TestCase
from django.urls import reverse

from tracker.models import Request


class ListRequestTests(TestCase):
    def test_shows_all_requests(self):
        Request.objects.create(title='Leaking tap')
        Request.objects.create(title='Broken chair')
        response = self.client.get(reverse('list_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_list.html')
        self.assertContains(response, 'Leaking tap')
        self.assertContains(response, 'Broken chair')

    def test_shows_message_when_empty(self):
        response = self.client.get(reverse('list_request'))
        self.assertContains(response, 'No requests yet.')

    def test_filters_by_multiple_urgency_levels(self):
        Request.objects.create(title='level1Urgent', urgency=1)
        Request.objects.create(title='level2Urgent', urgency=2)
        Request.objects.create(title='level3Urgent', urgency=3)
        response = self.client.get(reverse('list_request'),{'level1Urgent': 'on', 'level3Urgent': 'on',})
        self.assertContains(response, 'level1Urgent')
        self.assertContains(response, 'level3Urgent')
        self.assertNotContains(response, 'level2Urgent')


class ViewRequestTests(TestCase):
    def test_shows_request(self):
        service_request = Request.objects.create(title='Leaking tap', description='Kitchen sink')
        response = self.client.get(reverse('view_request', args=[service_request.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_detail.html')
        self.assertContains(response, 'Leaking tap')
        self.assertContains(response, 'Kitchen sink')

    def test_missing_request_returns_404(self):
        response = self.client.get(reverse('view_request', args=[999]))
        self.assertEqual(response.status_code, 404)


class CreateRequestTests(TestCase):
    def test_shows_empty_form(self):
        response = self.client.get(reverse('create_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_form.html')
        self.assertContains(response, 'New request')

    def test_valid_post_creates_request_and_redirects(self):
        response = self.client.post(reverse('create_request'), {'title': 'Leaking tap', 'description': 'Kitchen sink', 'urgency': 1})
        service_request = Request.objects.get()
        self.assertEqual(service_request.title, 'Leaking tap')
        self.assertRedirects(response, reverse('view_request', args=[service_request.pk]))

    def test_invalid_post_shows_errors_and_creates_nothing(self):
        response = self.client.post(reverse('create_request'), {'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Request.objects.count(), 0)


class UpdateRequestTests(TestCase):
    def setUp(self):
        self.service_request = Request.objects.create(title='Leaking tap', description='Kitchen sink')
        self.url = reverse('update_request', args=[self.service_request.pk])

    def test_shows_form_with_current_values(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_form.html')
        self.assertContains(response, 'Edit request')
        self.assertContains(response, 'value="Leaking tap"')

    def test_valid_post_updates_request_and_redirects(self):
        response = self.client.post(self.url, {'title': 'Dripping tap', 'description': 'Bathroom', 'urgency': 1})
        self.service_request.refresh_from_db()
        self.assertEqual(self.service_request.title, 'Dripping tap')
        self.assertEqual(self.service_request.description, 'Bathroom')
        self.assertRedirects(response, reverse('view_request', args=[self.service_request.pk]))

    def test_invalid_post_shows_errors_and_changes_nothing(self):
        response = self.client.post(self.url, {'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.service_request.refresh_from_db()
        self.assertEqual(self.service_request.title, 'Leaking tap')

    def test_missing_request_returns_404(self):
        response = self.client.get(reverse('update_request', args=[999]))
        self.assertEqual(response.status_code, 404)


class DeleteRequestTests(TestCase):
    def setUp(self):
        self.service_request = Request.objects.create(title='Leaking tap')
        self.url = reverse('delete_request', args=[self.service_request.pk])

    def test_get_shows_confirmation_and_deletes_nothing(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_confirm_delete.html')
        self.assertContains(response, 'Leaking tap')
        self.assertTrue(Request.objects.filter(pk=self.service_request.pk).exists())

    def test_post_deletes_request_and_redirects(self):
        response = self.client.post(self.url)
        self.assertFalse(Request.objects.filter(pk=self.service_request.pk).exists())
        self.assertRedirects(response, reverse('list_request'))

    def test_missing_request_returns_404(self):
        response = self.client.post(reverse('delete_request', args=[999]))
        self.assertEqual(response.status_code, 404)


class EscapingTests(TestCase):
    """User input must be shown as text, never run as HTML or JavaScript."""

    def setUp(self):
        self.service_request = Request.objects.create(
            title='<script>alert("title")</script>',
            description='<script>alert("description")</script>',
        )

    def test_list_page_escapes_input(self):
        response = self.client.get(reverse('list_request'))
        self.assertNotContains(response, '<script>alert(')
        self.assertContains(response, '&lt;script&gt;alert(')

    def test_detail_page_escapes_input(self):
        response = self.client.get(reverse('view_request', args=[self.service_request.pk]))
        self.assertNotContains(response, '<script>alert(')
        self.assertContains(response, '&lt;script&gt;alert(&quot;title&quot;)')
        self.assertContains(response, '&lt;script&gt;alert(&quot;description&quot;)')

    def test_edit_form_escapes_input(self):
        response = self.client.get(reverse('update_request', args=[self.service_request.pk]))
        self.assertNotContains(response, '<script>alert(')

    def test_delete_page_escapes_input(self):
        response = self.client.get(reverse('delete_request', args=[self.service_request.pk]))
        self.assertNotContains(response, '<script>alert(')


class LinkTests(TestCase):
    """Each page links to the right pages for the right request."""

    def setUp(self):
        self.first = Request.objects.create(title='First')
        self.second = Request.objects.create(title='Second')

    def assertLinksTo(self, response, url_name, *args):
        self.assertContains(response, f'href="{reverse(url_name, args=args)}"')

    def test_list_page_links_each_request_to_its_pages(self):
        response = self.client.get(reverse('list_request'))
        for service_request in [self.first, self.second]:
            self.assertLinksTo(response, 'view_request', service_request.pk)
            self.assertLinksTo(response, 'update_request', service_request.pk)
            self.assertLinksTo(response, 'delete_request', service_request.pk)
        self.assertLinksTo(response, 'create_request')

    def test_detail_page_links_to_its_own_edit_and_delete_pages(self):
        response = self.client.get(reverse('view_request', args=[self.second.pk]))
        self.assertLinksTo(response, 'update_request', self.second.pk)
        self.assertLinksTo(response, 'delete_request', self.second.pk)
        self.assertLinksTo(response, 'list_request')
        self.assertNotContains(response, reverse('update_request', args=[self.first.pk]))

    def test_delete_page_cancel_returns_to_request(self):
        response = self.client.get(reverse('delete_request', args=[self.second.pk]))
        self.assertLinksTo(response, 'view_request', self.second.pk)

    def test_form_cancel_returns_to_list(self):
        response = self.client.get(reverse('create_request'))
        self.assertLinksTo(response, 'list_request')

    def test_every_page_has_navbar_links(self):
        urls = [
            reverse('list_request'),
            reverse('create_request'),
            reverse('view_request', args=[self.first.pk]),
            reverse('update_request', args=[self.first.pk]),
            reverse('delete_request', args=[self.first.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'Maintenance request tracker')
                self.assertLinksTo(response, 'list_request')
                self.assertLinksTo(response, 'create_request')


class DetailDisplayTests(TestCase):
    def test_shows_placeholder_when_description_is_empty(self):
        service_request = Request.objects.create(title='Broken chair', description='')
        response = self.client.get(reverse('view_request', args=[service_request.pk]))
        self.assertContains(response, 'No description.')

    def test_hides_placeholder_when_description_is_present(self):
        service_request = Request.objects.create(title='Broken chair', description='Leg snapped')
        response = self.client.get(reverse('view_request', args=[service_request.pk]))
        self.assertNotContains(response, 'No description.')

    def test_line_breaks_in_description_are_shown(self):
        service_request = Request.objects.create(title='Leaking tap', description='First line\nSecond line')
        response = self.client.get(reverse('view_request', args=[service_request.pk]))
        self.assertContains(response, 'First line<br>Second line')

    def test_list_page_shortens_long_descriptions(self):
        Request.objects.create(title='Leaking tap', description='x' * 100)
        response = self.client.get(reverse('list_request'))
        self.assertNotContains(response, 'x' * 100)
        self.assertContains(response, 'x' * 79 + '…')


class IdDisplayTests(TestCase):
    """The request's id is shown on the pages for a single request."""

    def setUp(self):
        self.service_request = Request.objects.create(title='Leaking tap')
        self.id_text = f'Request #{self.service_request.id}'

    def test_detail_page_shows_id(self):
        response = self.client.get(reverse('view_request', args=[self.service_request.id]))
        self.assertContains(response, self.id_text)

    def test_edit_form_shows_id(self):
        response = self.client.get(reverse('update_request', args=[self.service_request.id]))
        self.assertContains(response, self.id_text)

    def test_edit_form_shows_id_after_invalid_submit(self):
        response = self.client.post(reverse('update_request', args=[self.service_request.id]), {'title': ''})
        self.assertContains(response, self.id_text)

    def test_delete_page_shows_id(self):
        response = self.client.get(reverse('delete_request', args=[self.service_request.id]))
        self.assertContains(response, self.id_text)

    def test_new_request_form_shows_no_id(self):
        response = self.client.get(reverse('create_request'))
        self.assertNotContains(response, 'Request #')