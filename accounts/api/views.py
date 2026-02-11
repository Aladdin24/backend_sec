# accounts/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView


#------------------------------------- User Profile Views -----------------------------------
@extend_schema(
    summary="Récupérer le profil utilisateur",
    description="Retourne les informations publiques de l'utilisateur connecté.",
    tags=['Authentification'],
    responses={
        200: OpenApiResponse(
            description="Profil récupéré",
            examples=[
                {
                    "email": "user@exemple.com",
                    "public_key": "-----BEGIN PUBLIC KEY-----...",
                    "is_active": True,
                    "date_joined": "2026-01-01T12:00:00Z"
                }
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        'id': str(user.id),
        'email': user.email,
        'public_key': user.public_key,
        'is_active': user.is_active,
        'date_joined': user.date_joined,
        'must_change_password': user.must_change_password
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user = request.user
    public_key = request.data.get('public_key')
    
    if public_key and public_key != user.public_key:
        user.public_key = public_key
        user.save(update_fields=['public_key'])
    
    return Response({
        'email': user.email,
        'public_key': user.public_key,
    })


#------------------------------ Change Password View -----------------------------------
@extend_schema(
    summary="Changer le mot de passe",
    description="L'utilisateur doit fournir son ancien mot de passe pour en définir un nouveau.",
    tags=['Authentification'],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "old_password": {"type": "string", "example": "AncienMotDePasse123!"},
                "new_password": {"type": "string", "example": "NouveauMotDePasse456!"},
                "confirm_password": {"type": "string", "example": "NouveauMotDePasse456!"}
            },
            "required": ["old_password", "new_password", "confirm_password"]
        }
    },
    responses={
        200: OpenApiResponse(description="Mot de passe mis à jour"),
        400: OpenApiResponse(description="Erreur de validation")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    user = request.user

    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    # Vérifier champs obligatoires
    if not old_password or not new_password or not confirm_password:
        return Response(
            {'error': 'Tous les champs sont obligatoires'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Vérifier ancien mot de passe
    if not user.check_password(old_password):
        return Response(
            {'error': 'Ancien mot de passe incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Vérifier correspondance des mots de passe
    if new_password != confirm_password:
        return Response(
            {'error': 'Les nouveaux mots de passe ne correspondent pas'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validation Django (longueur, complexité, etc.)
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response(
            {'error': e.messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Sauvegarde
    user.set_password(new_password)
    user.save(update_fields=['password'])

    return Response(
        {'message': 'Mot de passe mis à jour avec succès'},
        status=status.HTTP_200_OK
    )

#------------------------------ Register Public Key View -----------------------------------

class RegisterPublicKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        public_key = request.data.get('public_key')

        if not public_key:
            return Response(
                {'error': 'Public key required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user.public_key = public_key
        user.save(update_fields=['public_key'])

        return Response(
            {'message': 'Public key registered'},
            status=status.HTTP_200_OK
        )



#------------------------------ Update Must Change Password Flag View -----------------------------------
@extend_schema(
    summary="Mettre à jour le drapeau de changement obligatoire de mot de passe",
    description="Met à jour le drapeau 'must_change_password' de l'utilisateur connecté à False après un changement de mot de passe réussi.",
    tags=['Authentification'],
    responses={
        200: OpenApiResponse(description="Drapeau mis à jour avec succès")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_must_change_password_flag(request):
    """
    Désactive le flag must_change_password pour l'utilisateur actuel.
    Appelé après un changement de mot de passe réussi.
    """
    try:
        request.user.must_change_password = False
        request.user.save(update_fields=['must_change_password'])
        return Response({'status': 'success', 'message': 'Flag mis à jour'})
    except Exception as e:
        return Response(
            {'error': 'Erreur lors de la mise à jour du flag'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
User = get_user_model()
@extend_schema(
    summary="Récupérer un utilisateur par email",
    description="Retourne les informations publiques d'un utilisateur donné son email.",
    tags=['Utilisateurs'],
    responses={
        200: OpenApiResponse(
            description="Utilisateur récupéré",
            examples=[
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "<EMAIL>",
                    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
                }
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_email(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Utilisateur introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not user.public_key:
        return Response(
            {'error': 'Utilisateur sans clé publique'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        'id': str(user.id),
        'email': user.email,
        'public_key': user.public_key
    })