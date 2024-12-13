from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from translator.models import Translation
from translator.serializers import TranslationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import google.generativeai as genai

# Create your views here.

class AllTranslation(APIView):

    language_source_param = openapi.Parameter(
        'langue_source', openapi.IN_QUERY, description="Langue source (ex: 'FR')", type=openapi.TYPE_STRING
    )
    language_target_param = openapi.Parameter(
        'langue_target', openapi.IN_QUERY, description="Langue cible (ex: 'EN')", type=openapi.TYPE_STRING
    )
    text_param = openapi.Parameter(
        'text', openapi.IN_QUERY, description="Texte à traduire", type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[language_source_param, language_target_param, text_param])
    def get(self, request):

        source = request.GET.get('langue_source')
        target = request.GET.get('langue_target')

        if source and target:
            result = Translation.objects.filter(langue_source=source.upper(), langue_target=target.upper())
        else:
            result = Translation.objects.all()

        serialized_data = TranslationSerializer(result, many=True)
        return Response(data=serialized_data.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        
        try:
            langue_source = request.GET.get('langue_source')
            langue_target = request.GET.get("langue_target")
            text = request.GET.get("text")

            if not langue_source or not langue_target or not text:
                return Response({"error": "Tous les champs (langue_source, langue_target, text) sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

            api_key = api_key # Mettre votre api_key ici
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            genai.configure(api_key=api_key)

            prompt = f"""
            Traduis {text} qui est en {langue_source} en {langue_target}. La réponse ne doit contenir que la traduction
            """
            response = model.generate_content(prompt)

            target_text = response.text.replace("\n", "")
            
            Translation.objects.create(
                source_language=langue_source,
                source_text=text,
                target_language=langue_target,
                target_text=target_text
            )

            return Response(data ={
                "Resultat": "Traduction ajoutée.",
                "Traduction": target_text
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Erreur lors de la traduction : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def index(request):
    return render(request, 'index.html', context={})