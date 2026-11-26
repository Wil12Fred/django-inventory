from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from .models import Orden, Pedido, Producto, Proveedor, ProveedorProducto


class LoggedInTestCase(TestCase):
    fixtures = ['data_sprint3_01']

    def setUp(self):
        get_user_model().objects.create_user('demo', password='demo-pass-123')
        self.client.login(username='demo', password='demo-pass-123')


class ListPagesTest(LoggedInTestCase):
    def test_products_page_lists_fixture_products(self):
        response = self.client.get('/productos/')
        self.assertEqual(response.status_code, 200)
        producto = Producto.objects.get(pk=1)
        self.assertContains(response, producto.nombre)
        self.assertContains(response, '/eliminar_producto/1/')

    def test_suppliers_page_lists_fixture_suppliers(self):
        response = self.client.get('/proveedores/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['proveedores']), 20)
        self.assertContains(response, 'Aliqua')
        self.assertContains(response, '/proveedor_producto/1/')

    def test_warehouses_page(self):
        response = self.client.get('/almacenes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['almacenes']), 10)

    def test_orders_page_lists_every_sales_order(self):
        response = self.client.get('/ordenes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ordenes']), 25)

    def test_supplier_report_counts_purchase_orders(self):
        response = self.client.get('/reporte_proveedores/')
        self.assertEqual(response.status_code, 200)
        rows = response.context['proveedores']
        self.assertEqual(sum(count for _, _, count in rows), Pedido.objects.count())

    def test_supplier_products_page(self):
        enlace = ProveedorProducto.objects.first()
        response = self.client.get('/proveedor_producto/%d/' % enlace.proveedor_id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(enlace.producto, list(response.context['productos']))

    def test_chart_api_returns_twelve_months(self):
        response = self.client.get('/api/chart/data/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['labels']), 12)
        self.assertEqual(len(data['default']), 12)


class AbcAnalysisTest(LoggedInTestCase):
    def test_each_row_names_the_product_of_its_order(self):
        response = self.client.get('/analisisabc/')
        self.assertEqual(response.status_code, 200)
        rows = response.context['ordenes']
        self.assertEqual(len(rows), Orden.objects.count())
        expected = sorted((o.producto.nombre, o.cantidad) for o in Orden.objects.all())
        self.assertEqual(sorted((nombre, cantidad) for nombre, cantidad, _, _ in rows), expected)

    def test_largest_order_is_class_a(self):
        rows = self.client.get('/analisisabc/').context['ordenes']
        mayor = Orden.objects.order_by('-cantidad').first()
        fila = [r for r in rows if r[1] == mayor.cantidad][0]
        self.assertEqual(fila[0], mayor.producto.nombre)
        self.assertEqual(fila[3], 'A')


class AuthRequiredTest(TestCase):
    fixtures = ['data_sprint3_01']

    def test_anonymous_cannot_delete_a_product(self):
        response = self.client.post('/eliminar_producto/1/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/iniciar_sesion', response['Location'])
        self.assertTrue(Producto.objects.filter(pk=1).exists())

    def test_reports_require_login(self):
        for url in ['/ordenes/', '/analisisabc/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)


class CreateAndDeleteTest(LoggedInTestCase):
    def test_register_supplier(self):
        response = self.client.post('/registrar_proveedor/', {
            'nombre': 'Nuevo', 'telefono': '5551234',
            'direccion': 'Av. Siempre Viva', 'correo': 'nuevo@example.com'})
        self.assertRedirects(response, '/inicio/')
        self.assertTrue(Proveedor.objects.filter(nombre='Nuevo',
                                                 correo='nuevo@example.com').exists())

    def test_register_supplier_rejects_bad_email(self):
        response = self.client.post('/registrar_proveedor/', {
            'nombre': 'Nuevo', 'telefono': '5551234',
            'direccion': 'x', 'correo': 'not-an-email'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Proveedor.objects.filter(nombre='Nuevo').exists())

    def test_register_product(self):
        response = self.client.post('/registrar_producto/', {
            'nombre': 'Tornillo', 'codigo': 'T-01', 'valor': '12',
            'fecha_ingreso_year': '2017', 'fecha_ingreso_month': '5',
            'fecha_ingreso_day': '20'})
        self.assertRedirects(response, '/inicio/')
        producto = Producto.objects.get(nombre='Tornillo')
        self.assertEqual(producto.codigo, 'T-01')
        self.assertEqual(str(producto.fecha_ingreso), '2017-05-20')

    def test_delete_product_asks_then_deletes(self):
        response = self.client.get('/eliminar_producto/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Producto.objects.filter(pk=1).exists())
        response = self.client.post('/eliminar_producto/1/')
        self.assertRedirects(response, '/inicio/')
        self.assertFalse(Producto.objects.filter(pk=1).exists())


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class RegisterPurchaseOrderTest(LoggedInTestCase):
    def _post(self):
        # the form caps both names at 20 characters
        producto = Producto.objects.get(pk=4)
        proveedor = Proveedor.objects.get(pk=1)
        datos = {'producto': producto.nombre, 'proveedor': proveedor.nombre,
                 'cantidad': '7'}
        for campo in ('fecha_prevista', 'fecha_recibida', 'fecha_realizada'):
            datos.update({campo + '_year': '2017', campo + '_month': '5',
                          campo + '_day': '20'})
        return producto, proveedor, self.client.post('/registrar_pedido/', datos)

    def test_creates_the_order_and_redirects(self):
        antes = Pedido.objects.count()
        producto, proveedor, response = self._post()
        self.assertRedirects(response, '/inicio/')
        self.assertEqual(Pedido.objects.count(), antes + 1)
        pedido = Pedido.objects.latest('id')
        self.assertEqual(pedido.producto, producto)
        self.assertEqual(pedido.proveedor, proveedor)
        self.assertEqual(pedido.cantidad, '7')

    def test_emails_the_supplier(self):
        producto, proveedor, _ = self._post()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [proveedor.correo])
        self.assertEqual(mail.outbox[0].subject, '[Pedido] - ' + producto.nombre)
        self.assertIn('Cantidad: 7', mail.outbox[0].body)
