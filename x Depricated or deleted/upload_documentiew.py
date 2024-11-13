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
            return redirect('ai-analysis', document_id=document.id)
        
    return render(request, 'app/upload-documents.html')
