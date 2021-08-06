import os
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import moviepy.video.io.ImageSequenceClip
from evolutionary_game_theory import one_replica_simulation, _compute_all_payoffs, _fermi_updating_rule


def _plot_time_serie(G, T, steps, x0, beta, ax, color):
    """
    Plots a single time-series

    Parameters
    ----------
    G : nx.Graph
    T : float
        Parametrized value of he payoff matrix
    steps : int
        Numebr of time-steps
    x0 : float
        Initial density of cooperators
    beta : float
        Models the importance of the difference of payoffs in a game
    ax : ax
    color: str
        Color of the plot

    Returns
    -------
    p : float
        Mean density
    """
    W = np.array([[1, 2 - T], [T, 0]])
    p, time_series = one_replica_simulation(G, W, steps, x0, beta, stationary=0.0)
    ax.plot(time_series, c=color, label=f'T = {T}')
    return p


def plot_time_series(G, steps, x0, beta, title, saving_path=False):
    """
    Makes times series plots

    Parameters
    ----------
    G : nx.Graph
    steps : int
        Number of steps
    x0 : float
        Initial density of cooperators
    beta : float
        Models the importance of the difference of payoffs in a game
    title : str
        Title of the plot
    saving_path : bool, default False
        If True, the image will be saved

    """
    means_dict = dict()
    plt.figure(figsize=(10, 5))
    ax = plt.gca()
    for T, c in tuple(zip(np.linspace(11, 19, 5), mcolors.TABLEAU_COLORS.keys())):
        p = _plot_time_serie(G, T / 10, steps=steps, x0=x0, beta=beta, ax=ax, color=c)
        means_dict[T / 10] = p
    plt.title(title)
    plt.xlabel('Time-steps')
    plt.ylabel('Proportion of nodes with cooperative strategy')
    plt.legend()
    if saving_path:
        plt.savefig('../reports/figures/time_series/' + title + '.jpeg', dpi=300)
    plt.show()

    plt.figure(figsize=(5, 5))
    plt.plot(list(means_dict.keys()), list(means_dict.values()), c='blue')
    plt.scatter(list(means_dict.keys()), list(means_dict.values()), c='blue')
    plt.title(title)
    plt.xlabel('T')
    plt.ylabel('Mean proportion of cooperative nodes')
    if saving_path is not None:
        plt.savefig('../reports/figures/states/' + title + '.jpeg', dpi=300)
    plt.show()


def make_simulation_video(G, W, steps, x0, beta, pos, name, fps=15):
    """
    Makes a video with the simulation evolution of the nodes strategies

    Parameters
    ----------
    G : nx.Graph
    W : array
        Payoff matrix
    steps : int
        Number of steps
    x0 : float
        Initial density of cooperators
    beta : float
        Models the importance of the difference of payoffs in a game
    pos : dict
        Position of each node
    name : str
        Name of the video
    fps : int

    """
    strategy = dict(zip(G.nodes(), np.random.choice([0, 1], len(G.nodes()), p=[x0, 1 - x0])))

    for t in range(steps):
        ### make plot
        plt.figure(figsize=(7, 5))
        ax = plt.gca()
        nx.draw(G, node_size=30, width=0.3, ax=ax, pos=pos,
                node_color=['red' if s == 0 else 'royalblue' for s in strategy.values()])
        plt.title('BA <500, 5> $x_0=0.2$ T=1.7')
        red_patch = mpatches.Patch(color='red', label='cooperative player')
        blue_patch = mpatches.Patch(color='royalblue', label='non-cooperative player')

        plt.legend(handles=[red_patch, blue_patch], loc='lower right')
        plt.savefig(f'../reports/figures/film/{name}/{t:04d}.png', dpi=300)
        plt.close()
        ###
        new_strategy = dict()
        payoffs = _compute_all_payoffs(G, W, strategy)
        for i in G.nodes():
            j = random.sample(list(G.neighbors(i)), 1)[0]  # random selected neighbor
            wi, wj = payoffs.get(i), payoffs.get(j)  # payoffs of each node
            pij = _fermi_updating_rule(wi, wj, beta)  # probability of node i to adopt j strategy
            if np.random.random() < pij:
                new_strategy[i] = strategy.get(j)
        strategy.update(new_strategy)  # update strategies

    # make video
    image_folder=f'../reports/figures/film/{name}'
    image_files = [image_folder+'/'+img for img in os.listdir(image_folder) if img.endswith(".png")]
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(sorted(image_files), fps=fps)
    clip.write_videofile(f'../reports/videos/{name}.mp4')