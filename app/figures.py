from flask import Response
import io
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

from app.common import COLORS
matplotlib.use('Agg')

params = {"ytick.color" : "w",
          "xtick.color" : "w",
          "axes.labelcolor" : "w",
          "axes.edgecolor" : "w"}
plt.rcParams.update(params)

def get_hist_image(data_points, user_points = None):

    binwidth = 100
    plt.figure(figsize = (6,5))
    ax = sns.histplot(
        data=data_points, 
        element="step"
    )
    
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.xlabel(r'Score', fontsize = 18)
    plt.ylabel(r'Joueurs', fontsize = 18)

    if user_points:
        dx = ax.get_xlim()[1]-ax.get_xlim()[0]
        dy = ax.get_ylim()[1]-ax.get_ylim()[0]

        ind = user_points
        lenArrow = dy/2
        lenHead = lenArrow/4
        wiArrow = dx/20
        n = lenArrow/2
        plt.arrow(
            ind, 
        #     n+lenArrow+lenHead, 
            lenArrow/20+lenArrow+lenHead,
            0, 
            -lenArrow, 
            head_width=wiArrow*2.5, 
            head_length=lenHead, 
            width=wiArrow, 
            fc='g', ec='k')

    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='png', dpi = 100, transparent=True)
    my_stringIObytes.seek(0)
    return Response(my_stringIObytes, mimetype=f'image/png')

def get_stats_image(data_points, labels):

    if not isinstance(data_points[0],list):
        data_points = [data_points]
        labels = [labels]


    colors = [c for _,c in COLORS.items()]
    print('>>'*100, colors)
    plt.figure(figsize = (8,6))
    for d,l,c in zip(data_points,labels,colors):
        print('++', c)
        sns.lineplot(
            data=d,
            label = l,
            color = c,
        )
    
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.xlabel(r'Jours', fontsize = 18)
    plt.ylabel(r'Gagnants', fontsize = 18)
    
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='png', dpi = 200, transparent=True)
    my_stringIObytes.seek(0)
    return Response(my_stringIObytes, mimetype=f'image/png')