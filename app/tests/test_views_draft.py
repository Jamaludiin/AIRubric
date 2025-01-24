from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Document, Analysis
import os

# run test 
# python manage.py test app.tests.test_views_draft

class AppViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('app-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')

    def test_dashboard_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/dashboard.html')

    def test_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('app-dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(reverse('login')))

    """def test_upload_document_view_post(self):
        self.client.login(username='testuser', password='testpassword')
        with open('test_document.pdf', 'wb') as f:
            f.write(b'%PDF-1.4 test content')

        with open('test_document.pdf', 'rb') as f:
            response = self.client.post(reverse('app-upload'), {'document': f})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Document.objects.filter(user=self.user).exists())
        os.remove('test_document.pdf')

    def test_upload_document_view_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('app-upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/upload-documents.html')

    def test_delete_document(self):
        self.client.login(username='testuser', password='testpassword')
        document = Document.objects.create(user=self.user, file='test.pdf', name='Test Document')

        response = self.client.post(reverse('app-delete-document', args=[document.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Document.objects.filter(id=document.id).exists())

    def test_ai_analysis_valid_document(self):
        self.client.login(username='testuser', password='testpassword')
        document = Document.objects.create(user=self.user, file='test.pdf', name='Test Document')

        response = self.client.get(reverse('app-ai-analysis', args=[document.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/AI-Analysis.html')

    def test_rename_document_post(self):
        self.client.login(username='testuser', password='testpassword')
        document = Document.objects.create(user=self.user, file='test.pdf', name='Test Document')

        response = self.client.post(reverse('app-rename-document', args=[document.id]), {'new_name': 'New Document Name'})
        document.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(document.name, 'New Document Name')

    def test_playground_upload_pdf(self):
        self.client.login(username='testuser', password='testpassword')
        with open('test_document.pdf', 'wb') as f:
            f.write(b'%PDF-1.4 test content')

        with open('test_document.pdf', 'rb') as f:
            response = self.client.post(reverse('app-playground'), {'pdf': f})

        self.assertEqual(response.status_code, 200)
        self.assertIn('PDF uploaded', str(response.content))
        os.remove('test_document.pdf')

    def test_review_result_view(self):
        self.client.login(username='testuser', password='testpassword')
        document = Document.objects.create(user=self.user, file='test.pdf', name='Test Document')
        analysis = Analysis.objects.create(document=document, result='Test result')

        response = self.client.get(reverse('app-review-result', args=[analysis.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/Review-Results.html')
   
    def test_dashboard_post_analysis(self):
        self.client.login(username='testuser', password='testpassword')
        document = Document.objects.create(user=self.user, file='document/test.pdf', name='Test Document')

        response = self.client.post(reverse('app-dashboard'), {'selected_document_id': document.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('success_message', response.context)
        self.assertTrue(Analysis.objects.filter(document=document).exists())
"""