from ..tutor.models import Tutor
from ..settings import YEAR
from .tutor import new_random_tutor
from .shirt import make_tshirt_options, make_tshirt_preferences

def populate_all(members, activations):
    new_tutors = members - Tutor.members.count()
    new_activations = int(new_tutors * activations)

    while new_tutors > 0:
        new_random_tutor(YEAR, new_activations > 0)

        new_tutors = new_tutors - 1
        new_activations = new_activations - 1

    make_tshirt_options()
    make_tshirt_preferences(0.8)
