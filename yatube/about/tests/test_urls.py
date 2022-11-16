from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def test_about_url_exists_at_desired_location(self):
        """Check that requests to /about/ pages are successful."""
        for address in self.urls_templates.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Check the templates for /about/ pages."""
        for address, template in self.urls_templates.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
