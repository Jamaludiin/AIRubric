# test_views.py: Test all views defined in views.py.
# run test 
# python manage.py test app.tests.test_views
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Document, Analysis

class ViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="password")
        
        # Create test data
        self.document = Document.objects.create(
            user=self.user,
            file="document/testfile.pdf",
            name="Test Document"
        )
        self.analysis = Analysis.objects.create(
            document=self.document,
            result="Analysis Result Text"
        )

        # Create a test client
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('app-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')

    def test_dashboard_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('app-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/dashboard.html')

    def test_playground_view(self):
        response = self.client.get(reverse('blog-playground'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/playground.html')

    def test_upload_document_view(self):
        self.client.login(username="testuser", password="password")
        with open('testfile.pdf', 'rb') as file:
            response = self.client.post(reverse('app-upload'), {'file': file})
        self.assertEqual(response.status_code, 302)  # Redirect after upload

    def test_ai_analysis_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('ai-analysis', args=[self.document.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analysis Result Text")

    def test_review_results_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('review-result', args=[self.analysis.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_document_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(reverse('app-delete', args=[self.document.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertEqual(Document.objects.count(), 0)

    def test_rename_document_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(reverse('rename-document', args=[self.document.id]), {
            'name': 'Renamed Document'
        })
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.name, 'Renamed Document')

    def test_questions_answers_view(self):
        response = self.client.get(reverse('questions-answers'))
        self.assertEqual(response.status_code, 200)

    def test_upload_question_document_view(self):
        self.client.login(username="testuser", password="password")
        with open('questionfile.pdf', 'rb') as file:
            response = self.client.post(reverse('app-upload-question-document'), {'file': file})
        self.assertEqual(response.status_code, 302)  # Redirect after upload
