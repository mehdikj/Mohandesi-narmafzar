from django.contrib import admin
from .models import Author, Category, Resource, ResourceFile
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin): list_display=("name","normalized_name"); search_fields=("name",)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): list_display=("name","parent"); search_fields=("name",)
class ResourceFileInline(admin.TabularInline): model=ResourceFile; extra=0; readonly_fields=("file_type","size_bytes","sha256","version","created_at")
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin): list_display=("title","status","access_policy","category","created_by","created_at"); list_filter=("status","access_policy"); search_fields=("title","publisher","isbn","keywords"); filter_horizontal=("authors",); inlines=(ResourceFileInline,)
@admin.register(ResourceFile)
class ResourceFileAdmin(admin.ModelAdmin): list_display=("resource","file_type","version","size_bytes","sha256","is_active"); readonly_fields=("file_type","size_bytes","sha256","version","created_at")
