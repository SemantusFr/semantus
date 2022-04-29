from flask import Response
import io
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')

params = {"ytick.color" : "w",
          "xtick.color" : "w",
          "axes.labelcolor" : "w",
          "axes.edgecolor" : "w"}
plt.rcParams.update(params)

def get_hist_image(data_points):

    plt.figure(figsize = (6,5))
    sns.histplot(data=data_points, element="step")
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.xlabel(r'Score', fontsize = 18)
    plt.ylabel(r'Joueurs', fontsize = 18)
    # plt.xlim([0, 1000])
    
    my_stringIObytes = io.BytesIO()
    # plt.savefig('test.png', format='png')
    plt.savefig(my_stringIObytes, format='png', dpi = 100, transparent=True)
    my_stringIObytes.seek(0)
    # my_base64_pngData = base64.b64encode(my_stringIObytes.read())
    # plain_data = base64.b64decode(data)
    return Response(my_stringIObytes, mimetype=f'image/png')