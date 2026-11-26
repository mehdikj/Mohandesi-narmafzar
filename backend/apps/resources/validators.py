import hashlib, zipfile
from pathlib import Path
from rest_framework import serializers
MAX_RESOURCE_FILE_SIZE=50*1024*1024

def validate_resource_file(upload):
    if not upload: raise serializers.ValidationError("A resource file is required.")
    if upload.size>MAX_RESOURCE_FILE_SIZE: raise serializers.ValidationError("File size exceeds the 50 MB Sprint 1 limit.")
    kind={".pdf":"PDF",".epub":"EPUB"}.get(Path(upload.name).suffix.lower())
    if not kind: raise serializers.ValidationError("Only PDF and EPUB files are allowed.")
    pos=upload.tell(); upload.seek(0); header=upload.read(8); upload.seek(pos)
    if kind=="PDF" and not header.startswith(b"%PDF-"): raise serializers.ValidationError("The uploaded file is not a valid PDF.")
    if kind=="EPUB":
        upload.seek(0)
        try:
            with zipfile.ZipFile(upload) as z: mimetype=z.read("mimetype")
            if mimetype!=b"application/epub+zip": raise serializers.ValidationError("The uploaded file is not a valid EPUB.")
        except (zipfile.BadZipFile,KeyError): raise serializers.ValidationError("The uploaded file is not a valid EPUB.")
        finally: upload.seek(pos)
    return kind

def sha256(upload):
    pos=upload.tell(); upload.seek(0); h=hashlib.sha256()
    for chunk in iter(lambda: upload.read(1024*1024),b""): h.update(chunk)
    upload.seek(pos); return h.hexdigest()
