"""Analyze and visualize."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List

BASE_DIR = '/home/novak/Desktop/CODE/cpisync/scripts/network_cpu_variations/.cpisync_0x'
BASE_DIR_2 = '/home/novak/Desktop/CODE/cpisync/scripts/network_cpu_variations/.cpisync_1x'
BASE_DIR_3 = '/home/novak/Desktop/CODE/cpisync/scripts/network_cpu_variations/.cpisync_2x'
DIRS = ['.cpisync_0', '.cpisync_01', '.cpisync_02',
        '.cpisync_03', '.cpisync_04', '.cpisync_05']
DIRS_2 = ['.cpisync_1', '.cpisync_2', '.cpisync_3',
          '.cpisync_4', '.cpisync_5', '.cpisync_6']
DIRS_3 = ['.cpisync_1', '.cpisync_2']
BANDWIDTHS = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006]

F_NAME = 'File Name'
B_SND = 'Bytes Transmitted'
B_RCV = 'Bytes Received'
COMM_T = 'Communication Time(s)'
IDLE_T = 'Idle Time(s)'
COMP_T = 'Computation Time(s)'


def set_style() -> None:
    bigger_size = 16

    plt.rc('pdf', fonttype=42)
    plt.rc('ps', fonttype=42)
    plt.rc('font', size=bigger_size)          # controls default text sizes
    plt.rc('axes', titlesize=bigger_size)     # fontsize of the axes title
    plt.rc('axes', labelsize=bigger_size)     # fontsize of the x and y labels
    plt.rc('xtick', labelsize=bigger_size)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=bigger_size)    # fontsize of the tick labels
    plt.rc('legend', fontsize=bigger_size)    # legend fontsize
    plt.rc('figure', titlesize=bigger_size)   # fontsize of the figure title

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"


def clear_style() -> None:
    plt.rcParams.update(plt.rcParamsDefault)
    plt.close()


class Observ:
    """
    Corresponds to one _observ.cpisync file.
    """

    def __init__(self, f_name='', b_snd=0, b_rcv=0, comm_t=0, idle_t=0, comp_t=0):
        self.f_name = f_name
        self.b_snd = b_snd
        self.b_rcv = b_rcv
        self.comm_t = comm_t
        self.idle_t = idle_t
        self.comp_t = comp_t

    def __str__(self):
        return json.dumps({F_NAME: self.f_name,
                           B_SND: self.b_snd,
                           B_RCV: self.b_rcv,
                           COMM_T: self.comm_t,
                           IDLE_T: self.idle_t,
                           COMP_T: self.comp_t})


def parse(dirpath: str) -> List[Observ]:
    """
    Parses all files from dirpath into their corresponding Observ objects.
    """

    all_obs = []

    for fle in sorted(Path(dirpath).iterdir(), key=os.path.getatime):
        if fle.name.endswith('_observ.cpisync'):
            with open('{}/{}'.format(dirpath, fle.name), 'r') as ffile:
                obs = Observ()
                obs.f_name = fle.name
                for line in ffile.readlines():
                    if line.startswith(B_SND):
                        obs.b_snd = int(line.split(':')[1].strip())
                    elif line.startswith(B_RCV):
                        obs.b_rcv = int(line.split(':')[1].strip())
                    elif line.startswith(COMM_T):
                        obs.comm_t = float(line.split(':')[1].strip())
                    elif line.startswith(IDLE_T):
                        obs.idle_t = float(line.split(':')[1].strip())
                    elif line.startswith(COMP_T):
                        obs.comp_t = float(line.split(':')[1].strip())

                all_obs.append(obs)

    return all_obs


def sum_time(observ: Observ) -> float:
    """Returns the sum of all times in an observation."""
    as_dict = json.loads(str(observ))
    stm = 0
    for key in as_dict.keys():
        if 'time' in key.lower():
            stm = stm + as_dict[key]

    return stm


def preprocess(base_dir: str, dirs: List[str]) -> List[List[float]]:
    """Prepares all data from the base dir."""
    per_dir_obs = []

    for ddir in dirs:
        all_files = parse(os.path.join(base_dir, ddir))
        dir_summary_times = []               # summary times in this dir
        for observ in all_files:
            summary_time = sum_time(observ)  # summary time in one file
            dir_summary_times.append(summary_time)

        per_dir_obs.append(dir_summary_times)

    return per_dir_obs


def cpisync_bad_better_optimal_mbar():
    """
    Plots CPISync total time to reconcile for 3 different mbar settings
    of which one is optimal (mbar == m). Bandwidth is on y axis.
    """
    set_style()

    # bandwidth in Kbps (original is in Mbps)
    bndw = [x * 1000 for x in [0.001, 0.002, 0.003, 0.004, 0.005, 0.006]]

    mbar_1024 = preprocess('DATA/CPISync',
                           ['{}/.cpisync'.format(x) for x in ['1', '2', '3', '4', '5', '6']])
    mbar_512 = preprocess('DATA/CPISync',
                          ['{}/.cpisync'.format(x) for x in ['7', '8', '9', '10', '11', '12']])
    mbar_opt = preprocess('DATA/CPISync_optimal',
                          ['{}/.cpisync'.format(x) for x in ['1', '2', '3', '4', '5', '6']])

    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_figheight(6)
    fig.set_figwidth(9)
    ax.set_xlabel('Bandwidth (Kbps)')
    ax.set_ylabel('Total time to reconcile (s)')

    # comment this for fig_11
    ax.errorbar(bndw, [np.mean(x) for x in mbar_1024],
                yerr=[np.std(x) for x in mbar_1024],
                fmt='o-', label=r'$\overline{m} = 1024$')

    ax.errorbar(bndw, [np.mean(x) for x in mbar_512],
                yerr=[np.std(x) for x in mbar_512],
                fmt='x-', label=r'$\overline{m} = 512$')

    ax.errorbar(bndw, [np.mean(x) for x in mbar_opt],
                yerr=[np.std(x) for x in mbar_opt],
                fmt='*-', label=r'$\overline{m} = m = 235$')

    ax.legend()
    plt.grid(linestyle='dotted')
    fig.tight_layout()
    plt.savefig('fig_1.pdf')
    plt.close()

    clear_style()


def cpisync_optimal_vs_iblt_optimal():
    """
    Plots total time to reconcile for optimal parameters
    in CPISync and IBLTSync. Bandwidth is on y axis.
    """
    set_style()

    # bandwidth in Kbps (original is in Mbps)
    bndw = [x * 1000 for x in [0.001, 0.002, 0.003, 0.004, 0.005, 0.006]]

    cpisync_opt = preprocess('DATA/CPISync_optimal',
                             ['{}/.cpisync'.format(x) for x in ['1', '2', '3', '4', '5', '6']])
    iblt_opt = preprocess('DATA/IBLTSync_optimal',
                             ['{}/.cpisync'.format(x) for x in ['1', '2', '3', '4', '5', '6']])

    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_figheight(6)
    fig.set_figwidth(9)
    ax.set_xlabel('Bandwidth (Kbps)')
    ax.set_ylabel('Total time to reconcile (s)')

    ax.errorbar(bndw, [np.mean(x) for x in cpisync_opt],
                yerr=[np.std(x) for x in cpisync_opt],
                fmt='o-', label=r'$\overline{m} = m = 235$')

    ax.errorbar(bndw, [np.mean(x) for x in iblt_opt],
                yerr=[np.std(x) for x in iblt_opt],
                fmt='x-', label=r'$hedge = 1.5, hashes = 4$')

    ax.legend()
    plt.grid(linestyle='dotted')
    fig.tight_layout()
    plt.savefig('fig_2.pdf')
    plt.close()

    clear_style()


def main():
    set_style()

    per_dir_obs = preprocess(BASE_DIR, DIRS)
    per_dir_obs_2 = preprocess(BASE_DIR_2, DIRS_2)
    per_dir_obs_3 = preprocess(BASE_DIR_3, DIRS_3)

    # Visualization

    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_figheight(6)
    fig.set_figwidth(9)
    ax.set_xlabel('Bandwidth (Kbps)')
    ax.set_ylabel('Total time to reconcile (s)')

    bndw = [x * 1000 for x in BANDWIDTHS]  # conversion to Kbps

    ax.errorbar(bndw, [np.mean(x) for x in per_dir_obs],
                yerr=[np.std(x) for x in per_dir_obs],
                fmt='o-', label=r'$\overline{m} = 512$, cpus=cpuc=3.3%')

    ax.errorbar(bndw, [np.mean(x) for x in per_dir_obs_2],
                yerr=[np.std(x) for x in per_dir_obs_2],
                fmt='x-', label=r'$\overline{m} = 1024$, cpus=cpuc=3.3%')

    # # TODO: remove this eventually
    # for _ in range(len(per_dir_obs) - len(per_dir_obs_3)):
    #     per_dir_obs_3.append([0] * len(per_dir_obs[0]))

    # TODO: it should be all BANDWIDTHS eventually
    bndw_3 = bndw[:len(per_dir_obs_3)]

    ax.errorbar(bndw_3, [np.mean(x) for x in per_dir_obs_3],
                yerr=[np.std(x) for x in per_dir_obs_3],
                fmt='*:', label=r'$\overline{m} = 1024$, cpus=cpuc=1%')

    ax.legend()
    plt.grid(linestyle='dotted')
    fig.tight_layout()
    plt.savefig('fig.pdf')
    plt.close()

    clear_style()


if __name__ == '__main__':
    main()