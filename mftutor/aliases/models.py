from django.db import models
import logging

class Alias(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)

    def __str__(self):
        return "%s -> %s" % (self.source, self.destination)

    class Meta:
        ordering = ['source', 'destination']
        verbose_name = 'alias'
        verbose_name_plural = verbose_name + 'er'
        unique_together = (('source', 'destination'),)

def transitive_closure(u, edges, visited=None):
    if visited:
        visited = frozenset([u]).union(visited)
    else:
        visited = frozenset([u])

    result = frozenset([u])

    if u not in edges:
        return result

    for v in edges[u]:
        if v in visited:
            logging.warning("Cycle involving "+v)
        else:
            result = result.union(transitive_closure(v, edges, visited))

    return result

def resolve_alias(recipient):
    """Given a recipient, return the transitive closure of the alias graph."""
    aliases = {}
    for a in Alias.objects.all():
        if a.source not in aliases:
            aliases[a.source] = set()
        aliases[a.source].add(a.destination)

    return transitive_closure(recipient, aliases)

def resolve_alias_reversed(destination):
    """Given a destination, return all the recipients whose mail will be
    delivered to the destination."""
    aliases = {}
    for a in Alias.objects.all():
        if a.destination not in aliases:
            aliases[a.destination] = set()
        aliases[a.destination].add(a.source)

    return transitive_closure(destination, aliases)

def resolve_aliases_reversed(destinations):
    """Given a list of destinations, return the dictionary
    {k: resolve_alias_reversed(k) for d in destinations}."""

    aliases = {}
    for a in Alias.objects.all():
        if a.destination not in aliases:
            aliases[a.destination] = set()
        aliases[a.destination].add(a.source)

    return {
        d: transitive_closure(d, aliases)
        for d in destinations
    }
