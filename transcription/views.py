"""
index view
transcription view
"""
from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """
    render root
    """
    return render(request, 'index.html')

#pylint: disable=W0613
def transcription(request):
    """
    transcription response
    """
    # Votre logique pour gérer la transcription
    return JsonResponse({"status": "success", "message": "Transcription completed"})
