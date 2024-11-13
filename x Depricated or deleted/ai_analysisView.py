from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Document, Analysis
import groq
import os

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
                # Initialize Groq client
                groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
                
                # Read the PDF content
                with open(document.file.path, 'rb') as file:
                    pdf_content = file.read()
                
                # Create the prompt
                prompt = f"""
                Please analyze this document and provide marking based on the rubric:
                {pdf_content}
                
                Provide a detailed analysis and marking breakdown.
                """
                
                # Make the API call to Groq
                completion = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert academic marker. Analyze documents and provide detailed feedback based on rubrics."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model="mixtral-8x7b-32768",  # or another appropriate model
                    temperature=0.7,
                )
                
                result = completion.choices[0].message.content
                
                # Save the analysis
                analysis = Analysis.objects.create(
                    document=document,
                    result=result
                )
                
                return JsonResponse({
                    'status': 'complete', 
                    'redirect_url': f'/review-results/{analysis.id}/'
                })
                
            except Exception as e:
                print(f"Analysis error: {str(e)}")  # For debugging
                return JsonResponse({
                    'status': 'error', 
                    'message': str(e)
                })
        
        return render(request, 'app/AI-Analysis.html', {'document': document})
        
    except Document.DoesNotExist:
        return redirect('app-upload')