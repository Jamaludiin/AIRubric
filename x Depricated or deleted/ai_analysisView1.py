from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Document, Analysis
from .groq_Marking import mark_assignment

@login_required
def ai_analysis(request, document_id):
    try:
        document = Document.objects.get(id=document_id, user=request.user)
        
        # Check if analysis already exists
        existing_analysis = Analysis.objects.filter(document=document).first()
        if existing_analysis:
            return render(request, 'app/Review-Results.html', {
                'analysis': existing_analysis,
                'document': document,
                'result': existing_analysis.result
            })

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Process the document using the new marking function
                result = mark_assignment(document.file.path)
                
                # Save analysis results
                analysis = Analysis.objects.create(
                    document=document,
                    result=result
                )
                
                return JsonResponse({
                    'status': 'complete', 
                    'redirect_url': f'/review-results/{analysis.id}/'
                })
                
            except Exception as e:
                print(f"Analysis error: {str(e)}")
                return JsonResponse({
                    'status': 'error', 
                    'message': str(e)
                })
        
        return render(request, 'app/AI-Analysis.html', {'document': document})
        
    except Document.DoesNotExist:
        return redirect('app-upload')