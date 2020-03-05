import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go


def plot(var):
    sns.set_style("darkgrid")
    plt.plot(var)
    plt.show()


def distplot(var):
    sns.distplot(var)
    plt.show()


def plot_3d(x, y, z, xtitle, ytitle, ztitle):
    fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z,
                                       mode='markers')])
    fig.update_layout(scene=dict(
        xaxis_title=xtitle,
        yaxis_title=ytitle,
        zaxis_title=ztitle),
    )

    fig.show()
