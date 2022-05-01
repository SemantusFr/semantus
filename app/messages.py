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
    "Demande des conseils d'orthographe à Trump.",
    "Ce n'est pas dans mon dictionnaire.",
    "Tu as tapé au clavier avec tes poings&nbsp;?",
    "Connais pas."
]

messages_not_top1000 = [
    "Pas dans le top 1000, et pas top du tout",
    "Ce n'est pas dans le top 1000 (ni dans le top 1000000&nbsp;!)",
    "Ouais mais en fait tu n'y es pas du tout...",
    "Sinon, t'as pas envie de vraiment essayer&nbsp;?",
    "Oulalalala, tu y étais presque&nbsp;! À quelques milliers de places près c'était bon&nbsp;!",
    "Genre, ça n'a rien à voir&nbsp;!",
    "Alors là, je dis non&nbsp;!",
    "Mais clairement pas...",
    "Trop à l'ouest.",
    "Touche le fond mais creuse encore.",
    "Aussi logique que Macron à la fête de l'huma.",
    "Tu es probablement doué·e à plein d'autres activités&nbsp;!",
    "Rien. À. Voir.",
    "Essaie encore&nbsp;!",
    "Ouaaaaaaiiiiis, mais non.",
    "On joue au même jeu là&nbsp;?",
    "Kamoulox&nbsp;!",
    "Nope.",
    "Tu es froid.",
    "Pas du tout&nbsp;!",
    "Oublie et va prendre l'air."
]

message_success = [
    "Trop de la balle&nbsp;!",
    "Avoue&nbsp;! Tu as triché&nbsp;?",
    "Gagné&nbsp;! Allez, va vite narguer tes collègues&nbsp;!",
    "Super&nbsp;! Mais Martine de la compta a été plus rapide...",
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
    "On se rapproche&nbsp;!",
]

messages_top1000 = [
    "Bien mais pas top.",
    "C'est cool, mais il y en a encore plein d'autres avant le bon",
    "Oulala, tu es super tiède&nbsp;!",
    "Je suis à court de réplique, mains continue&nbsp;!",
    "Sur la bonne voie&nbsp;!",
    "Aller&nbsp;! Encore un gros effort&nbsp;!",
    "AB, continue comme ça.",
    "Tu as raison, on y va doucement.",
    "Bien.",
    "OK, mais faudrait penser à accélérer un peu.",
    "Je crois que Martine à la compta a bientôt trouvé.",
    "Je dis oui, mais pas trop fort.",
    "Pas si mal.",
    "Pourquoi pas.",
    "Mouais.",
    "Y a un vague lien...",
    "Ça me dis vaguement quelque chose.",
    "Oui, mais encore&nbsp;?",
    "Et, donc&nbsp;?",
    "Tu crois que tu auras terminé avant de tirer la chasse&nbsp;?",
]