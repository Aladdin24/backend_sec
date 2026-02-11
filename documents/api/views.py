# documents/api/views.py
from urllib.parse import urlparse

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from documents.models import Document, Category, DocumentAccess
from accounts.models import User

@api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
@permission_classes([permissions.IsAuthenticated])

def list_categories(request):
    categories = Category.objects.all().values('id', 'name', 'description')
    return Response(categories)


# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def upload_document(request):
#     """
#     Exemple de payload :
#     {
#       "filename": "contrat.pdf",
#       "storage_path": "secure/abc123.enc",
#       "file_hash": "a1b2c3...",
#       "signature": "base64...",
#       "mime_type": "application/pdf",
#       "category_id": "uuid-cat",
#       "shared_with": [
#         {"user_id": "uuid1", "encrypted_aes_key": "base64..."},
#         {"user_id": "uuid2", "encrypted_aes_key": "base64..."}
#       ]
#     }
#     """
#     data = request.data

#     # Vérifier catégorie
#     category = None
#     if data.get('category_id'):
#         category = get_object_or_404(Category, id=data['category_id'])

#     # Créer le document
#     doc = Document.objects.create(
#         filename=data['filename'],
#         storage_path=data['storage_path'],
#         file_hash=data['file_hash'],
#         signature=data['signature'],
#         mime_type=data.get('mime_type', ''),
#         uploaded_by=request.user,
#         category=category
#     )

#     # Gérer le partage
#     shared_with = data.get('shared_with', [])
#     access_list = []
#     for item in shared_with:
#         user = get_object_or_404(User, id=item['user_id'])
#         access = DocumentAccess(
#             document=doc,
#             user=user,
#             encrypted_aes_key=item['encrypted_aes_key']
#         )
#         access_list.append(access)

#     # Ajouter l'utilisateur lui-même
#     access_list.append(
#         DocumentAccess(
#             document=doc,
#             user=request.user,
#             encrypted_aes_key=data.get('owner_encrypted_aes_key', '')  # Optionnel
#         )
#     )

#     DocumentAccess.objects.bulk_create(access_list)

#     return Response({
#         'id': doc.id,
#         'message': 'Document uploadé et partagé avec succès'
#     }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_documents(request):
    """
    Retourne tous les documents accessibles par l'utilisateur,
    groupés par catégorie.
    """
    # Récupérer tous les documents où l'utilisateur a accès
    accessible_doc_ids = DocumentAccess.objects.filter(
        user=request.user
    ).values_list('document_id', flat=True)

    documents = Document.objects.filter(
        id__in=accessible_doc_ids
    ).select_related('category', 'uploaded_by')

    # Grouper par catégorie
    from collections import defaultdict
    grouped = defaultdict(list)

    for doc in documents:
        access = DocumentAccess.objects.get(document=doc, user=request.user)
        cat_name = doc.category.name if doc.category else "Sans catégorie"
        grouped[cat_name].append({
            'id': str(doc.id),
            'filename': doc.filename,
            'mime_type': doc.mime_type,

            'uploaded_by': {
                'email': doc.uploaded_by.email,
                'public_key': doc.uploaded_by.public_key
            },
            # 'uploaded_by': doc.uploaded_by.email,
            'uploaded_at': doc.created_at.isoformat(),
            'file_hash': doc.file_hash,
            'signature': doc.signature,
            'storage_path': doc.storage_path,
            'encrypted_aes_key': access.encrypted_aes_key,

        })

    return Response(dict(grouped))



#----------------------------------------------Share Document-----------------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_document(request, document_id):
    """
    Payload :
    {
      "shared_with": [
        {"user_id": "uuid", "encrypted_aes_key": "base64"}
      ]
    }
    """
    doc = get_object_or_404(Document, id=document_id)

    # Seul le propriétaire peut partager
    if doc.uploaded_by != request.user:
        return Response(
            {'error': 'Seul le propriétaire peut partager ce document'},
            status=status.HTTP_403_FORBIDDEN
        )

    shared_with = request.data.get('shared_with', [])
    access_list = []
    for item in shared_with:
        user = get_object_or_404(User, id=item['user_id'])
        # Éviter les doublons
        if not DocumentAccess.objects.filter(document=doc, user=user).exists():
            access = DocumentAccess(
                document=doc,
                user=user,
                encrypted_aes_key=item['encrypted_aes_key']
            )
            access_list.append(access)

    if access_list:
        DocumentAccess.objects.bulk_create(access_list)

    return Response({'message': f'{len(access_list)} utilisateurs ajoutés'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_users(request):
    users = User.objects.exclude(id=request.user.id).values('id', 'email', 'public_key')
    return Response(users)



#--------------------------------------------Download Document----------------------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_document(request, document_id):
    """
    Retourne les métadonnées + une URL pré-signée pour télécharger
    un document chiffré auquel l'utilisateur a accès.
    """
    # 1. Vérifier l'accès
    doc = get_object_or_404(Document, id=document_id)
    access = get_object_or_404(DocumentAccess, document=doc, user=request.user)

    # 2. Vérifier la configuration S3
    required_settings = [
        'AWS_S3_ENDPOINT_URL',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    for setting in required_settings:
        if not hasattr(settings, setting) or not getattr(settings, setting):
            return Response(
                {'error': 'Stockage objet non configuré'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 3. Créer le client S3
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
        use_ssl=getattr(settings, 'AWS_S3_USE_SSL', True),
        verify=getattr(settings, 'AWS_S3_VERIFY', True),
    )

    # 4. Générer l'URL pré-signée
    try:
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': doc.storage_path
            },
            ExpiresIn=3600
        )
        
        # ✅ CORRECTION : Ne PAS modifier l'URL pour Backblaze
        # Seulement pour MinIO local (développement)
        if hasattr(settings, 'MINIO_PUBLIC_URL') and settings.DEBUG:
            parsed = urlparse(download_url)
            download_url = download_url.replace(
                f"{parsed.scheme}://{parsed.netloc}",
                settings.MINIO_PUBLIC_URL
            )
            
    except ClientError as e:
        return Response(
            {'error': f'Erreur stockage: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 5. Répondre avec les métadonnées
    return Response({
        'document_id': str(doc.id),
        'filename': doc.filename,
        'mime_type': doc.mime_type,
        'download_url': download_url,
        'file_hash': doc.file_hash,
        'signature': doc.signature,
        'encrypted_aes_key': access.encrypted_aes_key,
        'uploaded_by': {
            'email': doc.uploaded_by.email,
            'public_key': doc.uploaded_by.public_key
        },
        'uploaded_at': doc.created_at
    })



#--------------------------------------------Delete Document----------------------------------------
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_document(request, document_id):
    doc = get_object_or_404(Document, id=document_id)
    
    if doc.uploaded_by != request.user:
        return Response(
            {'error': 'Seul le propriétaire peut supprimer ce document'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    doc.delete()  # Supprime aussi les DocumentAccess (CASCADE)
    return Response({'message': 'Document supprimé'}, status=status.HTTP_204_NO_CONTENT)



#----------------------------------------Prepare Upload Document--------------------------------------
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import uuid
import os
from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(
    summary="Préparer un upload vers MinIO",
    description="Génère une URL pré-signée pour uploader un fichier chiffré directement vers MinIO.",
    tags=['Documents'],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "example": "rapport.pdf"}
            },
            "required": ["filename"]
        }
    },
    responses={
        200: OpenApiResponse(
            description="URL générée",
            examples=[{
                "upload_url": "http://minio:9000/secure-docs/abc123_rapport.pdf?X-Amz-Signature=...",
                "storage_path": "abc123_rapport.pdf"
            }]
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def prepare_upload(request):
    """
    Génère une URL pré-signée pour l'upload direct vers MinIO/Backblaze B2.
    """
    # 1. Vérifier la configuration S3
    required_settings = [
        'AWS_S3_ENDPOINT_URL',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    for setting in required_settings:
        if not hasattr(settings, setting) or not getattr(settings, setting):
            return Response(
                {'error': 'Stockage objet non configuré'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 2. Valider le nom de fichier
    filename = request.data.get('filename')
    if not filename:
        return Response(
            {'error': 'Le champ "filename" est requis'},
            status=status.HTTP_400_BAD_REQUEST
        )

    filename = os.path.basename(filename)
    if not filename or filename.startswith('.') or any(c in filename for c in '/\\'):
        return Response(
            {'error': 'Nom de fichier invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Générer un nom unique
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    # 4. Créer le client S3
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
        use_ssl=getattr(settings, 'AWS_S3_USE_SSL', True),
        verify=getattr(settings, 'AWS_S3_VERIFY', True),
    )

    # 5. Générer l'URL pré-signée
    try:
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket, 'Key': unique_name},
            ExpiresIn=600,
            HttpMethod='PUT'
        )
        
        # ✅ CORRECTION : Ne PAS modifier l'URL pour Backblaze
        # Backblaze retourne déjà une URL publique valide
        # Seulement pour MinIO local, on remplace l'endpoint
        if hasattr(settings, 'MINIO_PUBLIC_URL') and settings.DEBUG:
            parsed = urlparse(upload_url)
            upload_url = upload_url.replace(
                f"{parsed.scheme}://{parsed.netloc}",
                settings.MINIO_PUBLIC_URL
            )
            
    except ClientError as e:
        return Response(
            {'error': f'Erreur génération URL: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({
        'upload_url': upload_url,
        'storage_path': unique_name
    })


#-----------------------------Confirm Upload Document(remplace upload_document)--------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_upload(request):
    """
    Confirmer l'upload après que le fichier a été envoyé à MinIO.
    Payload :
    {
      "storage_path": "abc123_doc.pdf",
      "filename": "doc.pdf",
      "file_hash": "...",
      "signature": "...",
      "mime_type": "...",
      "category_id": "...",
      "shared_with": [...]
    }
    """
    data = request.data
    storage_path = data.get('storage_path')
    if not storage_path:
        return Response({'error': 'storage_path requis'}, status=400)

    # Vérifier que le fichier existe dans MinIO (optionnel mais sécurisant)
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    try:
        s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=storage_path)
    except ClientError:
        return Response({'error': 'Fichier non trouvé dans le stockage'}, status=400)

    # Puis créer le Document (comme avant)
    category = None
    if data.get('category_id'):
        category = get_object_or_404(Category, id=data['category_id'])

    doc = Document.objects.create(
        filename=data['filename'],
        storage_path=storage_path,  # ex: "abc123_doc.pdf"
        file_hash=data['file_hash'],
        signature=data['signature'],
        mime_type=data.get('mime_type', ''),
        uploaded_by=request.user,
        category=category
    )

    # Partage (comme avant)
    shared_with = data.get('shared_with', [])
    access_list = []
    for item in shared_with:
        user = get_object_or_404(User, id=item['user_id'])
        access_list.append(DocumentAccess(
            document=doc,
            user=user,
            encrypted_aes_key=item['encrypted_aes_key']
        ))
    # Ajouter l'uploader
    access_list.append(DocumentAccess(
        document=doc,
        user=request.user,
        encrypted_aes_key=data.get('owner_encrypted_aes_key', '')
    ))
    DocumentAccess.objects.bulk_create(access_list)

    return Response({'id': doc.id, 'message': 'Document confirmé'}, status=201)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_category(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Nom requis'}, status=400)
    
    if Category.objects.filter(name__iexact=name).exists():
        return Response({'error': 'Catégorie existe déjà'}, status=400)
    
    category = Category.objects.create(name=name.strip())
    return Response({
        'id': str(category.id),
        'name': category.name
    }, status=201)