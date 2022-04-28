from random import choice

def get_message_from_score(score):
    if score == 1000:
        return choice(message_success)
    elif score > 990:
        return choice(messages_top10)
    elif score > 900:
        return choice(messages_top100)
    elif score > 0:
        return choice(messages_top1000)
    elif score == 0:
        return choice(messages_not_top1000)
    else:
        return choice(message_not_word)

message_not_word = [
    "C'est du du Polonais&nbsp;?",
    "Non mais sinon, tu veux pas essayer des mots français&nbsp;?",
    "C'est du français&nbsp;?",
    "Aussi vrai que <i>ptdr</i> c'est du français",
    "N'oublie pas que ça doit être au singulier masculin...",
    "T'as pas un petit cousin de 6 ans qui peut te proposer des vrais mots&nbsp;?",
    "¿&nbsp;Hablas francés&nbsp;?",
    "ты говоришь по французски&nbsp;?",
    "Demande des conseils d'orthographe à Trump."
]

messages_not_top1000 = [
    "Pas dans le top 1000, et pas top du tout",
    "Ce n'est pas dans le top 1000 (ni dans le top 1000000&nbsp;!)",
    "Ouais mais en fait tu n'y est pas du tout...",
    "Sinon, t'as pas envie de vraiment essayer&nbsp;?",
    "Oulalalala, tu y étais presque&nbsp;! À quelque milliers de place près c'était bon&nbsp;!",
    "Genre, ça n'a rien à voir&nbsp;!",
    "Alors là, je dis non&nbsp;!",
    "Mais clairement pas...",
    "Trop à l'ouest.",
    "Touche le fond mais creuse encore.",
    "Aussi logique que Macron à la fête de l'huma.",
    "Tu est probablement doué·e à plein d'autres activités&nbsp;!",
    "Rien. n'a. voir.",
    "Essaie encore&nbsp;!"
]

message_success = [
    "Trop de la balle&nbsp;!",
    "Avoue&nbsp;! Tu as triché&nbsp;?",
]

messages_top10 = [
    "Pas mal du tout !",
    "Encore un petit effort&nbsp;!",
    "Pas mal ! Et dire qu'il va te falloir encore 97 essais...",
    "Chaud chaud chaud&nbsp;!!! (Cacao)",
    "Tu es dans le top 10&nbsp;!",
]

messages_top100 = [
    "On se rapproche...",
    "Tu chauffes&nbsp;!",
    "Bonne direction&nbsp;!",
    "Creuse encore un peu cette idée.",
    "Fonce !",
    "Tu es dans le top 100&nbsp;!",
]

messages_top1000 = [
    "Bien mais pas top.",
    "C'est cool, mais il y en a encore plein d'autres avant le bon",
    "Oulala, tu es super tiède !",
    "Je suis à court de réplique, mains continue !",
    "Sur la bonne voie !",
    "Aller ! Encore un gros effort !",
    "AB, continue comme ça.",
    "Tu as raison, on y va doucement.",
    "Bien.",
    "OK, mais faudrait penser à accélérer un peu.",
    "Je crois que Martine à la compta a bientôt trouvé.",
    "Je dis oui, mais pas trop fort.",

]