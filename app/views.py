from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .ChatPDF_Groq import ask_pdf as ask_pdf_groq
from .CrewAI_LangChain import crew_result
from .models import Document, Analysis
import os

from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
from .groq_Marking import mark_assignment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse  
# Assuming you have a Document model
from .models import Document
from django.contrib import messages



marking_prompt = """
    As a Professor marking this assignment critically, please evaluate using all the criterai set in the rubric provided in the document:

    see sample of response below:
    Marking the Smartphone Class Assignment
    Here is a breakdown of the marks for the Smartphone class assignment based on the provided rubric:
    Object Design (20%): Excellent (4)
    ●
    Comments: The object has six well-named attributes: brand, model, storageCapacity, ram, batteryCapacity, and screenSize. These are all appropriately typed using String, int, and double. The object also includes well-defined methods such as a constructor, getters and setters for each attribute, calculateBatteryLife, and displaySmartphoneDetails. The constructor and methods are properly documented with comments.
    Encapsulation (20%): Excellent (4)
    ●
    Comments: The assignment demonstrates excellent use of encapsulation. All attributes are declared as private, restricting direct access from outside the class. Access to these attributes is controlled through public getter and setter methods, ensuring data integrity and security.
    Main Class Implementation (20%): Excellent (4)
    ●
    Comments: The MainClass effectively uses control structures like the Scanner for input, if-else statements for decision making based on calculated battery life, and method calls to interact with the Smartphone object. The code is well-organized, readable, and free from errors. The implementation demonstrates strong programming skills in utilizing object-oriented principles.
    Creativity and Object Choice (20%): Good (3)
    ●
    Comments: While a smartphone is a relevant object to implement using OOP principles, it's a fairly common choice. The assignment would benefit from exploring slightly more unique or complex objects to showcase a deeper understanding of OOP. The attributes and methods are well-chosen and implemented, but could be expanded with more creative features.
    ○
    Improvement: Consider choosing an object that presents more unique challenges for data representation or behaviour. For example, a smart home system with interconnected devices, a library catalog system, or a simulation of a biological ecosystem. These options would allow for more creative use of inheritance, polymorphism, and complex relationships between objects.
    Documentation and Comments (10%): Excellent (4)
    ●
    Comments: The code is well-documented with clear explanations for each attribute, method, and control structure. Comments are concise and effectively provide insights into the code's functionality.
    Remarks: The assignment demonstrates a strong grasp of object-oriented programming concepts. The code is well-structured, readable, and functional. A slightly more creative object choice could further enhance the demonstration of OOP principles.
    Total Marks: 19 / 20



    For each category:
    - Assign a score (Excellent: score number, Good: score number, Fair: score number, Needs Improvement: score number)
    - Provide specific feedback in each question
    - Highlight strengths and areas for improvement in each question and specify the statements that are wrong or correct
    - Give practical suggestions for improvement in each question by specifying the statements that are wrong or correct

    state the following:
    student name:
    student id:
    assignment title:

    state the following for each question or category:
    Total Marks: score number / total marks e.g Final Score: 9/12 (75%)
    criticsm: mention the statements that are wrong or correct
    improvement: mention the statements that are wrong or correct and suggest improvements
    strengths: mention the statements that are correct
    remarks: overall remarks

    
    Format the response in HTML table with appropriate tags (<h2>, <p>, <ul>, etc.).
    Include a final score and overall remarks.
    """


def home(request):

    return render(request, 'app/home.html')


@login_required
def dashboard(request):
    documents = Document.objects.filter(user=request.user)
    output = None
    success_message = None
    error_message = None

    if request.method == "POST" and "selected_document_id" in request.POST:
        document_id = request.POST["selected_document_id"]
        try:
            document = Document.objects.get(id=document_id, user=request.user)
            analysis = document.analysis_set.first()
            
            if not analysis:
                # If no analysis exists, create one using ask_pdf_groq
                result = ask_pdf_groq(document.file.path, marking_prompt)
                analysis = Analysis.objects.create(
                    document=document,
                    result=result
                )
                success_message = "Analysis completed successfully."
            
            output = analysis.result
            
        except Document.DoesNotExist:
            error_message = "Document not found."
        except Exception as e:
            error_message = f"Error during analysis: {str(e)}"

    context = {
        'documents': documents,
        'output': output,
        'success_message': success_message,
        'error_message': error_message
    }
    return render(request, 'app/dashboard.html', context)




@login_required
@csrf_protect
def upload_document(request):
    if request.method == 'POST':
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            # Save the document
            document = Document.objects.create(
                user=request.user,
                file=uploaded_file,
                name=uploaded_file.name
            )
            # Redirect to analysis page
            return redirect('app-dashboard')
        
    return render(request, 'app/upload-documents.html')

@login_required
def ai_analysis(request, document_id):
    try:
        document = Document.objects.get(id=document_id, user=request.user)

         # First render the analysis page
        if request.method == 'GET':
            return render(request, 'app/AI-Analysis.html', {'document': document})
        

        # Process the document with Groq
        result = ask_pdf_groq(document.file.path, "do the marking of this assignment based on the rubric inside the document")
        
        # Save analysis results
        analysis = Analysis.objects.create(
            document=document,
            result=result
        )
        return redirect('review-result', analysis_id=analysis.id)
    except Document.DoesNotExist:
        return redirect('app-upload')



@login_required
def review_result(request, analysis_id):
    try:
        analysis = Analysis.objects.get(id=analysis_id, document__user=request.user)
        context = {
            'analysis': analysis,
            'document': analysis.document
        }
        return render(request, 'app/Review-Results.html', context)
    except Analysis.DoesNotExist:
        return redirect('app-upload')







# single pdf handler
@login_required
def playground(request):
    # Initialize path variable
    pdf_path = request.session.get('pdf_path')

    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)  # Save the file and get its name
        pdf_path = fs.path(filename)  # Get the correct path to the saved file on the server
        request.session['pdf_path'] = pdf_path  # Store the PDF path in session
        print(f"PDF uploaded: {pdf_path}")  # Debugging output

    output = ""
    if request.method == "POST" and request.POST.get('user_input'):
        user_input = request.POST.get('user_input')
        
        try:
            # Ensure a PDF file is uploaded before asking a question
            if pdf_path and os.path.exists(pdf_path):  # Check if file exists on the server
                output = ask_pdf_groq(pdf_path, user_input)  # Pass PDF path and user question to the function
    
            else:
                output = "Please upload a valid PDF file or input a prompt before asking questions."
        except Exception as e:
            output = f"Error: {e}"  # Handle errors and display them

    return render(request, 'app/playground.html', {
        'output': output,
        'user_input': request.POST.get('user_input', ''),
        'pdf_path': pdf_path
    })



@login_required
def delete_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id, user=request.user)
        # Delete the actual file from storage
        if document.file:
            if os.path.exists(document.file.path):
                os.remove(document.file.path)
        
        # Delete the database record
        document.delete()
        messages.success(request, 'Document successfully deleted.')
        return redirect('app-delete')
    except Document.DoesNotExist:
        messages.error(request, 'Document not found.')
        return redirect('app-dashboard')


@login_required
def rename_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id, user=request.user)
        if request.method == 'POST':
            new_name = request.POST.get('new_name')
            if new_name:
                document.name = new_name
                document.save()
                messages.success(request, 'Document renamed successfully.')
            return render(request, 'app/rename-document.html')
        
    except Document.DoesNotExist:
        messages.error(request, 'Document not found.')
    return redirect('app-dashboard')
