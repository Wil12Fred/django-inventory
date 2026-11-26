from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Producto


class SmokeTest(TestCase):
    fixtures = ['data_sprint3_01']

    def setUp(self):
        get_user_model().objects.create_user('demo', password='demo-pass-123')

    def test_login_page_renders(self):
        response = self.client.get('/iniciar_sesion/')
        self.assertEqual(response.status_code, 200)

    def test_pages_require_login(self):
        response = self.client.get('/productos/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/iniciar_sesion', response['Location'])

    def test_login_then_list_products(self):
        response = self.client.post(
            '/iniciar_sesion/?next=/productos/',
            {'username': 'demo', 'password': 'demo-pass-123'})
        self.assertRedirects(response, '/productos/')
        response = self.client.get('/productos/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Producto.objects.count(), 100)
        self.assertEqual(len(response.context['productos']), 100)

    def test_reports_render(self):
        self.client.login(username='demo', password='demo-pass-123')
        for url in ['/inicio/', '/proveedores/', '/almacenes/', '/pedidos/',
                    '/reporte_productos/', '/ordenes/', '/analisisabc/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
