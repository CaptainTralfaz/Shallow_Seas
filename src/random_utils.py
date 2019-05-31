from random import randint


def random_choice_index(chances):
    """
    Sum positive chances, pick random number between 1 and the sum, then return the index of the choice
    :param chances: list of positive chances
    :return: int index of choice
    """
    random_chance = randint(1, sum(chances))
    
    running_sum = 0
    choice = 0
    for w in chances:
        
        if random_chance <= running_sum:
            return choice
        choice += 1


def random_choice_from_dict(choice_dict):
    """

    :param choice_dict: dict containing key:choice value: chance to show up
    :return: str choice from choice_dict keys
    """
    choices = list(choice_dict.keys())
    positive_choices = [choice for choice in choices if choice_dict[choice] > 0]
    positive_chances = [choice_dict[choice] for choice in choices if choice_dict[choice] > 0]
    
    return positive_choices[random_choice_index(positive_chances)]
