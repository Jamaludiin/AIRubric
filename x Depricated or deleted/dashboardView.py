
def dashboard(request):
    output = ""

    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)
        pdf_path = fs.path(filename)
        request.session['pdf_path'] = pdf_path  # Store the PDF path in session
        print(f"PDF uploaded: {pdf_path}")  # Debugging output

        # Process the PDF and get feedback
        if os.path.exists(pdf_path):
            output = ask_pdf_groq(pdf_path, marking_prompt)
            #output = mark_assignment(pdf_path)
        else:
            output = "Error: The uploaded file could not be processed."

    return render(request, 'app/dashboard.html', {'output': output, 'pdf_path': pdf_path})

