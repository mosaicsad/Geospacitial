import matplotlib.pyplot as plt
from matplotlib import gridspec
from autograd import numpy as np
import os
import copy
import csv

def plot_two_sequences(seq1, seq2):
    # initialize figure
    fig = plt.figure(figsize=(10, 5))

    # create subplot with 3 panels, plot input function in center plot
    gs = gridspec.GridSpec(2, 1)
    ax1 = plt.subplot(gs[1])

    ax1.plot(np.arange(np.size(seq1)), seq1.flatten(), c='k', linewidth=2.5,label='sequence 1')
    ax1.plot(np.arange(np.size(seq2)), seq2.flatten(), c='lime', linewidth=2.5, label='sequence 1', zorder=2)

    # label axes and title
    #ax1.set_title('input sequence')
    #ax1.set_xlabel('step')

    plt.show()


path = '../../probe_data_map_matching/MatchedPointsSlope.csv'
if os.path.exists(path):
    with open(path, 'r') as f:
        original = []
        ourResult = []
        for i, line in enumerate(f):
            original.append(line[-1])
            ourResult.append(line[-2])
            if i % 100000 == 0:
                print(i)
        plot_two_sequences(np.array(original), np.array(ourResult))
        print('done')
else:
    print("not open file correctly!")