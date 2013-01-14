from django.db import models

class Alias(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.source)+' -> '+unicode(self.destination)

    class Meta:
        ordering = ['source', 'destination']
        verbose_name = 'alias'
        verbose_name_plural = verbose_name + 'er'
        unique_together = (('source', 'destination'),)
