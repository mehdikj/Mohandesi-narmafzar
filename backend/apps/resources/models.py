from django.conf import settings
from django.db import models
class Author(models.Model):
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, db_index=True)
    def save(self,*args,**kwargs): self.normalized_name=" ".join(self.name.split()).casefold(); super().save(*args,**kwargs)
    def __str__(self): return self.name
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    def __str__(self): return self.name
class Resource(models.Model):
    class Status(models.TextChoices): DRAFT="DRAFT","Draft"; PUBLISHED="PUBLISHED","Published"; ARCHIVED="ARCHIVED","Archived"
    class AccessPolicy(models.TextChoices): PUBLIC="PUBLIC","Public"; REGISTERED_ONLY="REGISTERED_ONLY","Registered only"; SUBSCRIPTION_LIMITED="SUBSCRIPTION_LIMITED","Subscription limited"; GROUP_SPECIFIC="GROUP_SPECIFIC","Group specific"; CONFIDENTIAL="CONFIDENTIAL","Confidential"
    title=models.CharField(max_length=500); authors=models.ManyToManyField(Author,blank=True,related_name="resources"); publisher=models.CharField(max_length=255,blank=True); publication_year=models.PositiveIntegerField(null=True,blank=True); language=models.CharField(max_length=50,blank=True); category=models.ForeignKey(Category,null=True,blank=True,on_delete=models.PROTECT,related_name="resources"); keywords=models.TextField(blank=True); description=models.TextField(blank=True); isbn=models.CharField(max_length=32,blank=True); cover_url=models.URLField(blank=True); status=models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT,db_index=True); access_policy=models.CharField(max_length=30,choices=AccessPolicy.choices,default=AccessPolicy.PUBLIC); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_resources"); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=("-created_at",)
    def __str__(self): return self.title
class ResourceFile(models.Model):
    class FileType(models.TextChoices): PDF="PDF","PDF"; EPUB="EPUB","EPUB"
    resource=models.ForeignKey(Resource,on_delete=models.PROTECT,related_name="files"); file=models.FileField(upload_to="resources/%Y/%m/"); file_type=models.CharField(max_length=10,choices=FileType.choices); size_bytes=models.PositiveBigIntegerField(); sha256=models.CharField(max_length=64,db_index=True); version=models.PositiveIntegerField(default=1); is_active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=("resource","version"),name="unique_resource_file_version")]
    def __str__(self): return f"{self.resource.title} v{self.version}"
