# documents/models.py
from django.db import models
from accounts.models import User
import uuid

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=512)  # ex: secure-docs/abc123.enc
    file_hash = models.CharField(max_length=64)      # SHA-256
    signature = models.TextField()                   # Base64
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    mime_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

class DocumentAccess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='accesses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_aes_key = models.TextField()  # Clé AES chiffrée avec clé publique de user

    class Meta:
        unique_together = ('document', 'user')