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
    "C'est du du Polonais ?",
    "Non mais sinon, tu veux pas essayer des mots français ?",
    "C'est du français ?",
    "Aussi vrai que <i>ptdr</i> c'est du français",
    "N'oublie pas que ça doit être au singulier masculin...",
    "T'as pas un petit cousin de 6 ans qui peut te proposer des vrais mots ?",
    "¿ Hablas francés ?",
    "ты говоришь по французски ?",
    "Demande des conseils d'orthographe à Trump."
]

messages_not_top1000 = [
    "Pas dans le top 1000, et pas top du tout",
    "Ce n'est pas dans le top 1000 (ni dans le top 1 000 000 !)",
    "Ouais mais en fait tu n'y est pas du tout...",
    "Sinon, t'as pas envie de vraiment essayer ?",
    "Oulalalala, tu y étais presque ! À quelque milliers de place près c'était bon !",
    "Genre ! Ça n'a rien à voir !",
    "Alors là, je dis non !",
    "Mais clairement pas...",
    "Trop à l'ouest.",
    "Touche le fond mais creuse encore.",
    "Aussi logique que Macron à la fête de l'huma.",
]

message_success = [
    "Trop de la balle !"
]

messages_top10 = [
    "Pas mal du tout !",
    "Encore un petit effort !",
    "Pas mal ! Et dire qu'il va te falloir encore 97 essais...",
    "Chaud chaud chaud !!! (Cacao)",
    "Tu es dans le top 10 !",
]

messages_top100 = [
    "On se rapproche...",
    "Tu chauffes !"
]

messages_top1000 = [
    "Bien mais pas top.",
    "C'est cool, mais il y en a encore plein d'autres avant le bon",
    "Oulala, tu es super tiède !",
    "Je suis à court de réplique, mains continue !",
    "Sur la bonne voie !",
    "Aller ! Encore un gros effort !",
    "AB, contitnue comme ça.",
    "Tu as raison, on y va doucement.",
    "Bien.",
    "OK, mais faudrait penser à accélérer un peu.",
    "Je crois que Martine à la compta a bientôt trouvé.",
    "Je dis oui, mais pas trop fort.",

]