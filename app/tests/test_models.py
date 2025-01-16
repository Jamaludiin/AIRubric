# test_models.py: Write tests for the models.py file here.
# run test 
# python manage.py test app.tests.test_models




from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Document, Analysis, Question


class DocumentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.document = Document.objects.create(
            user=self.user,
            file="document/testfile.pdf",
            name="Test Document"
        )

    def test_document_creation(self):
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(self.document.name, "Test Document")
        self.assertEqual(self.document.user.username, "testuser")

    def test_document_file_path(self):
        self.assertEqual(self.document.file, "document/testfile.pdf")


class AnalysisModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.document = Document.objects.create(
            user=self.user,
            file="document/testfile.pdf",
            name="Test Document"
        )
        self.analysis = Analysis.objects.create(
            document=self.document,
            result="Analysis Result Text"
        )

    def test_analysis_creation(self):
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(self.analysis.document.name, "Test Document")
        self.assertEqual(self.analysis.result, "Analysis Result Text")


class QuestionModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.document = Document.objects.create(
            user=self.user,
            file="document/testfile.pdf",
            name="Test Document"
        )
        self.question = Question.objects.create(
            question="What is Django?",
            answer="Django is a web framework.",
            user=self.user,
            document=self.document,
            chapter="Chapter 1",
            topic="Introduction",
            level="Easy",
            subject="Computer Science",
            bloom_taxon="1",
            file="question_document/samplefile.pdf",
            name="Test Question"
        )

    def test_question_creation(self):
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(self.question.question, "What is Django?")
        self.assertEqual(self.question.answer, "Django is a web framework.")
        self.assertEqual(self.question.chapter, "Chapter 1")
        self.assertEqual(self.question.level, "Easy")

    def test_question_associations(self):
        self.assertEqual(self.question.document.name, "Test Document")
        self.assertEqual(self.question.user.username, "testuser")
        self.assertEqual(self.question.file, "question_document/samplefile.pdf")
