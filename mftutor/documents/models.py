# coding: utf-8
from django.db import models
from ..settings import YEAR

# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length=100)
    year = models.IntegerField(verbose_name="Tutorår", default = YEAR)
    time_of_upload = models.DateTimeField(editable=False, auto_now_add=True)
    # type_choices must match the regex in urls.py
    type_choices = (("guides", "Guide"),("referater", "Referat"),("udgivelser","Udgivelse"))    
    type = models.CharField(max_length = 30, choices=type_choices)
    def doc_upload_to(instance,filename):
        return "docs/" + unicode(instance.year) + "/" +  instance.type + "/" + filename        
    doc_file = models.FileField(upload_to = doc_upload_to)
    class Meta:
        ordering = ("-year","title")
    def __unicode__(self):
        return '[Document '+self.type+': '+self.title+']'
  
    
    




