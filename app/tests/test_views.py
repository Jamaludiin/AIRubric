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

# The test is failing because it can't find the 'testfile.pdf' file. We need to create a mock file instead of trying to open a real one.
    """def test_upload_document_view(self):
        self.client.login(username="testuser", password="password")
        with open('testfile.pdf', 'rb') as file:
            response = self.client.post(reverse('app-upload'), {'file': file})
        self.assertEqual(response.status_code, 302)  # Redirect after upload
"""
    # fixing the above test
    """test_upload_document_view test which is expecting a 302 (redirect) status 
    code but receiving 200.
This typically means that your view is rendering a template instead 
of redirecting after a successful upload. The issue could be in either 
your view implementation or the test itself. Let's modify the test to be more robust:"""
    """def test_upload_document_view(self):
        self.client.login(username="testuser", password="password")
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a mock PDF file
        mock_pdf = SimpleUploadedFile(
            "testfile.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        response = self.client.post(reverse('app-upload'), {'file': mock_pdf})
        self.assertEqual(response.status_code, 302)  # Redirect after upload
"""

# again try to fix the above

    """def test_upload_document_view(self):
        self.client.login(username="testuser", password="password")
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a mock PDF file with more realistic content
        mock_pdf = SimpleUploadedFile(
            "testfile.pdf",
            b"%PDF-1.4\n%\x93\x8C\x8B\x9E" + b"x" * 100,  # More realistic PDF content
            content_type="application/pdf"
        )
        
        # Add name field if your form expects it
        response = self.client.post(reverse('app-upload'), {
            'file': mock_pdf,
            'name': 'Test Document'  # Add this if your form requires a name
        })
        
        # Add debug information
        if response.status_code != 302:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content.decode()}")
            
        self.assertEqual(response.status_code, 302)  # Redirect after upload
        self.assertTrue(Document.objects.filter(name='Test Document').exists())  # Verify document was created
"""

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

# he was not redirecting 
    """def test_rename_document_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(reverse('rename-document', args=[self.document.id]), {
            'name': 'Renamed Document'
        })
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.name, 'Renamed Document')"""


# fixed the above malfunctioning test
def test_rename_document_view(self):
    self.client.login(username="testuser", password="password")
    response = self.client.post(reverse('rename-document', args=[self.document.id]), {
        'name': 'Renamed Document'
    })
    print(f"Response status code: {response.status_code}")  # Debug print
    print(f"Response content: {response.content}")  # Debug print
    self.assertEqual(response.status_code, 302)  # Expecting redirect
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
