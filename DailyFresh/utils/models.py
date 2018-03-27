from django.db import models

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    isDelete = models.BooleanField(default=False)

    class Meta:
        abstract = True
<<<<<<< HEAD

=======
>>>>>>> 665b20e7f457edc4d588b7fe3b5281f4e73363e5
