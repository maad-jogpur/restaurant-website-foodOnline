from django.core.exceptions import ValidationError
import os

def allow_only_images_validators(file):
    ext = os.path.splitext(file.name)[1]
    print(ext)
    validated_extensions = ['.png','.jpg','jpeg']
    if ext.lower() not in validated_extensions:
        raise ValidationError("Unsupported File. Allowed file extensions: "+str(validated_extensions))
    

