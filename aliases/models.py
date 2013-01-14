from django.db import models
import logging

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

def resolve_alias(recipient, visited=None):
    """Given a recipient, return the transitive closure of the alias graph."""
    if visited:
        visited = frozenset([recipient]).union(visited)
    else:
        visited = frozenset([recipient])

    aliases = list(Alias.objects.filter(source=recipient))
    result = frozenset([recipient])
    for a in aliases:
        if a.destination in visited:
            logging.warning("Cycle involving "+a)
        else:
            result = result.union(resolve_alias(a.destination, visited))

    return result

def resolve_alias_reversed(destination, visited=None):
    """Given a destination, return all the recipients whose mail will be
    delivered to the destination."""
    if visited:
        visited = frozenset([destination]).union(visited)
    else:
        visited = frozenset([destination])

    aliases = list(Alias.objects.filter(destination=destination))
    result = frozenset([destination])
    for a in aliases:
        if a.source in visited:
            logging.warning("Cycle involving "+a)
        else:
            result = result.union(resolve_alias_reversed(a.source, visited))

    return result
