from ..tutor.models import Tutor
from ..settings import YEAR
from .tutor import new_random_tutor
from .shirt import make_tshirt_options, make_tshirt_preferences
from .confirmation import fill_out_confirmations

def populate_all(members):
    new_tutors = members - Tutor.members.count()

    while new_tutors > 0:
        new_random_tutor(YEAR)

        new_tutors = new_tutors - 1

    make_tshirt_options()
    make_tshirt_preferences(0.8)

    fill_out_confirmations(0.95)
