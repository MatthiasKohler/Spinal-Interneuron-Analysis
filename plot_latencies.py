#!/usr/bin/env python3

import numpy as np
import re
import glob
import itertools as it
from collections import defaultdict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd
import plot_style
from scipy.stats import variation

#p = re.compile('[a-zA-Z0-9/\-\_]+/([a-zA-Z0-9]+)\_([a-zA-Z0-9]+)\_([a-zA-Z]+)([0-9]+)\_([\-+][1-4])\_ampl\_([0-9]+)\.dat')

#Minium latencies per experiment
#min_latencies = defaultdict(lambda:100.0)

#avg_latencies = defaultdict(list)

p = re.compile('[a-zA-Z0-9/\-\_\.]+/([a-zA-Z0-9]+)\_([a-zA-Z0-9]+)\_([a-zA-Z]+)([0-9]+)\_([\-+][1-4])\_ampl\_([0-9]+)\.dat')

DR_latency_correction = 1.7 #ms

#Ia_Ib_1_Ex = 2.55 - DR_latency_correction #ms
#Ia_Ib_2_In = 4.1  - DR_latency_correction #ms

#DR_latencies = [2.3, 3.5, 4.8]
skin_epsp_latencies = [1.0, 5.0]
skin_ipsp_latencies = [0.7, 5.0]
dr_epsp_latencies   = [2.3]
dr_ipsp_latencies   = [0.9]

dr_epsp_Ia_Ib_seperation = [0.85, 3.5]
dr_ipsp_Ia_Ib_seperation = [2.4]

def decompose_filename(f):
    m = p.match(f)

    if m is None:
        print('No match: ', f)
        return None

    return {'ID':          m.group(1), 
            'description': m.group(2).lower(), 
            'source':      ''.join(sorted(m.group(3).lower())), 
            'stimulation': int(m.group(4)), 
            'synaptology': int(m.group(5)), 
            'amp':         int(m.group(6))}


class PSP:
    def __init__(self, filename, synaptology_table):
        file_attributes = decompose_filename(filename)

        if file_attributes is None:
            self.valid = False
            return
        else:
            self.valid = True

        self.filename = filename

        self.ID, \
        self.description, \
        self.source, \
        self.stimulation, \
        self.synaptology, \
        self.amp          =  file_attributes.values()

        Skinlatency_table = synaptology_table[synaptology_table.ID == self.ID].Skinlatency
        self.Skinlatency = next(iter(Skinlatency_table), 101010.0)
        #print(self.Skinlatency)
        if(self.Skinlatency > 100):
            print(self.ID)

        f = np.loadtxt(filename, dtype = float, delimiter = ',')

        if f.shape[1] == 3:
            f = f[[x[0] > 0 for x in f]]
            self.latencies = f[:,0]
            self.amplitude = f[:,1]
        elif f.shape[1] == 4:
            f = f[[x[1] > 0 for x in f]]
            self.latencies = f[:,1]
            self.amplitude = f[:,2]
        else:
            self.valid = False
            return

        if self.source in ["ikns", "rs", "iklnnsu"]:
            self.latencies = self.latencies - self.Skinlatency
        elif self.source in ['dr']:
            self.latencies = self.latencies - DR_latency_correction
        else:
            print('Unknown source')

        self.avg_latency = np.mean(self.latencies)
        self.var_latency = np.var(self.latencies)
        self.min_latency = np.min(self.latencies)
        self.max_latency = np.max(self.latencies)

        self.avg_amplitude = np.mean(self.amplitude)
        self.var_amplitude = np.var(self.amplitude)
        self.min_amplitude = np.min(self.amplitude)
        self.max_amplitude = np.max(self.amplitude)

    def __str__(self):
        return self.ID + " " + \
               self.description + " " + \
               self.source + " " + \
               str(self.stimulation) + " " + \
               "syn:" + str(self.synaptology) + " " + \
               "amp:" + str(self.amp) + " " + \
               "avg_latency:" + str(self.avg_latency) + " " +\
               "var_latency:" + str(self.var_latency)
    


def get_PSPs(files, synaptology_file):
    ret = []
    for f in files:
        psp = PSP(f, synaptology_file)
        if psp.valid:
            ret.append(psp)
    return ret

def get_latencies(psps, synaptology = True, ID = False, filename = False):
    avg_latencies = []
    var_latencies = []
    label_texts = []
    synaptologies = []

    for psp in psps:
        if(psp.Skinlatency > 100):
            continue

        avg_latencies.append(psp.avg_latency)

        var_latencies.append(psp.var_latency)

        label_text = ""#str(psp.stimulation) 
        #if synaptology:
        #    label_text += str(np.abs(psp.synaptology))
        #if ID:
        #   label_text += " " + str(psp.ID)
        #if filename:
        #   label_text += " " + psp.filename
        label_texts.append(label_text)

        synaptologies.append(psp.synaptology)
 
    return avg_latencies, var_latencies, label_texts, synaptologies


def plot_latencies(psps, filename, vlines = [], labels = True, title = None):
    avg_latencies, var_latencies, label_texts, synaptologies = get_latencies(psps)

    #fig = plt.figure() #figsize=(3,3),dpi=300)
    fig = plt.figure(figsize = (3, 1.5), dpi = 300)
    ax = fig.add_subplot(111)
  
    plot_style.hide_spines(ax)
    ax.set_xlim(0, 10.0)
    #ax.set_ylim(-0.1, 3.5)
    ax.set_xlabel("Average latency [ms]", fontsize = 9)
    ax.set_ylabel("Latency variance", fontsize = 9)
    plt.yscale("log")
    ax.set_title(filename if title is None else title, fontsize = 9)
    ax.tick_params(axis='both', which='major', labelsize=9)

    #xy = np.vstack([avg_latencies, var_latencies])
    #colors = gaussian_kde(xy, bw_method = 0.1)(xy)
    #sns.kdeplot(avg_latencies, var_latencies, ax = ax, bw = 0.1, cmap = 'Reds')

    for l, v, s in zip(avg_latencies, var_latencies, synaptologies):
        color = 'red' if s < 0 else 'black'
        ax.scatter(l, v, s = 10, zorder = 2, color = color)
        if s < 0 and l < 0.2:
            print(l, v, s)

    #fig.colorbar(bar)
    
    for x in vlines:
        ax.axvline(x)
    
    if labels:
        for x, y, label in zip(avg_latencies, var_latencies, label_texts):
            ax.text(x, y + 0.1, label, fontsize = 4, rotation = 0)
    

    fig.savefig('./plots_latencies/' + filename + '.pdf', bbox_inches='tight', dpi = 300)


def plot_latencies_hist(psps, filename, vlines = [], labels = True, bw = 0.1, color = 'black', title = None):
    avg_latencies, var_latencies, label_texts, _ = get_latencies(psps, filename = False)
    
    fig = plt.figure(figsize = (3, 1.5), dpi = 300)
    ax = fig.add_subplot(111)

    plot_style.hide_spines(ax)
    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 0.65)
    ax.set_title(filename if title is None else title, fontsize = 9)
    ax.set_xlabel("Latency [ms]", fontsize = 9)
    ax.set_ylabel("Density", fontsize = 9)
    ax.tick_params(axis='both', which='major', labelsize=9)


    sns.kdeplot(avg_latencies, shade = True, ax = ax, bw = bw, color = color)

    random_offset = []
    for _ in avg_latencies:
        random_offset.append(np.random.uniform(0.0, 0.02))
    random_offset = np.array(random_offset)

    ax.scatter(avg_latencies, random_offset + 0.1, s = 2, color = color)

    if labels:
        offset = 10 * random_offset + 0.2
        for x, y, label in zip(avg_latencies, offset, label_texts):
            ax.text(x, y, label, fontsize = 1, rotation = 90)

    #ax.errorbar(avg_latencies, 3 * random_offset + 0.3, xerr = np.array(var_latencies) / 5, capsize = 2, elinewidth = 1, fmt = ',k')

    for x, linestyle in vlines:
        ax.axvline(x, linestyle = linestyle)

    fig.savefig('./plots_latencies/hist_' + filename + '.pdf', bbox_inches='tight', dpi = 300)
    

def generate_latency_plots():
    files = glob.glob('./data_raw/' + '/**/*.dat', recursive=True)
    
    synaptology_file = pd.read_csv("./data_synaptology/Synaptology_HQ_tidy.csv")
    #print(synaptology_file)
    psps = get_PSPs(files, synaptology_file)

    sources = set()

    #i = 0
    #for psp in psps:
    #    print(i, psp.source)
    #    sources.add(psp.source)
    #    i += 1
    #print(sources)

    ipsp_filter = lambda l: filter(lambda psp: psp.synaptology < 0, l)
    epsp_filter = lambda l: filter(lambda psp: psp.synaptology > 0, l)
    dr_filter   = lambda l: filter(lambda psp: psp.source in ["dr"], l)    
    skin_filter = lambda l: filter(lambda psp: psp.source in ["ikns", "rs", "iklnnsu"], l)

    #threshold_filter = lambda th, l: filter(lambda psp: psp.stimulation < th, l)


    ipsps = list(ipsp_filter(psps))
    epsps = list(epsp_filter(psps))

    dr_ipsps   = list(dr_filter(  ipsp_filter(psps)))
    dr_epsps   = list(dr_filter(  epsp_filter(psps)))
    skin_ipsps = list(skin_filter(ipsp_filter(psps)))
    skin_epsps = list(skin_filter(epsp_filter(psps)))

    dr_psps    = list(dr_filter(psps))
    skin_psps  = list(skin_filter(psps))

    Ia_mono_epsps = list(filter(lambda psp: psp.avg_latency < dr_epsp_Ia_Ib_seperation[0]                          , dr_epsps))
    Ib_mono_epsps = list(filter(lambda psp: dr_epsp_Ia_Ib_seperation[0] <= psp.avg_latency <= dr_epsp_latencies[0] , dr_epsps))

    Ia_di_ipsps = list(filter(lambda psp: psp.avg_latency <  dr_ipsp_Ia_Ib_seperation[0] , dr_ipsps))
    Ib_di_ipsps = list(filter(lambda psp: dr_ipsp_Ia_Ib_seperation[0] <= psp.avg_latency , dr_ipsps))

    Ia_psps = Ia_mono_epsps + Ia_di_ipsps
    Ib_psps = Ib_mono_epsps + Ib_di_ipsps

    #plot_latencies(skin_ipsps, "avg_var_skin_ipsps_labeled")
    #plot_latencies(skin_epsps, "avg_var_skin_epsps_labeled")
    #plot_latencies(dr_ipsps,   "avg_var_dr_ipsps_labeled", vlines = dr_ipsp_Ia_Ib_seperation)
    #plot_latencies(dr_epsps,   "avg_var_dr_epsps_labeled", vlines = dr_epsp_Ia_Ib_seperation)

    #plot_latencies(skin_ipsps, "avg_var_skin_ipsps", labels = True)
    #plot_latencies(skin_epsps, "avg_var_skin_epsps", labels = True)
    #plot_latencies(dr_ipsps,   "avg_var_dr_ipsps",   labels = True)
    #plot_latencies(dr_epsps,   "avg_var_dr_epsps",   labels = True)

    plot_latencies(dr_psps,    "avg_var_dr_psps",    labels = True, title = "DR PSPs")
    plot_latencies(skin_psps,  "avg_var_skin_psps",  labels = True, title = "Skin PSPs")

    plot_latencies_hist(skin_ipsps, "skin_ipsps", vlines = list(it.product(skin_ipsp_latencies, ['solid'])),
                        labels = False, bw = 0.2, color = 'red', title = 'Skin IPSPs')

    plot_latencies_hist(skin_epsps, "skin_epsps", vlines = list(it.product(skin_epsp_latencies, ['solid'])),
                        labels = False, bw = 0.2, color = 'black',   title = 'Skin EPSPs')

    plot_latencies_hist(dr_ipsps,   "dr_ipsps",   vlines = list(it.product(dr_ipsp_latencies, ['-']))
                                                         + list(it.product(dr_ipsp_Ia_Ib_seperation, ['--'])),
                        labels = False, bw = 0.2, color = 'red', title = 'DR IPSPs')

    plot_latencies_hist(dr_epsps,   "dr_epsps",   vlines = list(it.product(dr_epsp_latencies, ['-']))
                                                         + list(it.product(dr_epsp_Ia_Ib_seperation, ['--'])),
                        labels = False, bw = 0.1, color = 'black',   title = 'DR EPSPs')

    #plot_latencies_hist(skin_ipsps, "skin_ipsps_labeled", labels = True, bw = 0.2, color = 'black', title = 'Skin IPSPs')
    #plot_latencies_hist(skin_epsps, "skin_epsps_labeled", labels = True, bw = 0.2, color = 'red',   title = 'Skin EPSPs')
    #plot_latencies_hist(dr_ipsps,   "dr_ipsps_labeled", labels = True, bw = 0.2, color = 'black', title = 'Deep Radial IPSPs')
    #plot_latencies_hist(dr_epsps,   "dr_epsps_labeled", labels = True, bw = 0.1, color = 'red',   title = 'Deep Radial EPSPs')

    #plot_latencies(Ia_mono_epsps, "Ia_epsps", labels = True)
    #plot_latencies(Ib_mono_epsps, "Ib_epsps", labels = True)
    #plot_latencies(Ia_di_ipsps, "Ia_ipsps", labels = True)
    #plot_latencies(Ib_di_ipsps, "Ib_ipsps", labels = True)

    #plot_latencies(Ia_psps, "Ia_psps", labels = True)
    #plot_latencies(Ib_psps, "Ib_psps", labels = True)


def analyze_amplitudes():
    files = glob.glob('./data_raw/' + '/**/*.dat', recursive=True)
    
    synaptology_file = pd.read_csv("./data_synaptology/Synaptology_HQ_tidy.csv")
    #print(synaptology_file)
    psps = get_PSPs(files, synaptology_file)

    slopes = []
    cvs = []
    supports = []
    support_neurons = []
    support_source = []

    for psp in psps:
        support = len(psp.amplitude)
        if support < 20:
            continue

        if psp.synaptology != 1:
            continue

        x = range(len(psp.amplitude))
        amp = psp.amplitude
        result = np.polyfit(x, amp, 1)
        slope = result[0]
        #print(result)

        if slope > 0.20:
            print("excessive slope", psp)

        slopes.append(slope)

        cv = variation(amp)

        if cv > 0.30:
            print(psp)
            print(psp.amplitude)


        cvs.append(cv)

        supports.append(support)
        if(psp.ID not in support_neurons):
            support_neurons.append(psp.ID)
        support_source.append(psp.source)

    slope_mean = np.mean(slopes)
    slope_cv = variation(slopes)
    slope_var = np.var(slopes)
    slope_standard_deviation = np.std(slopes)
    print("average slope", slope_mean)
    print("variance slope", slope_var)
    print("standard deviation slope", slope_standard_deviation)
    print("coefficient of variation slope", slope_cv)

    print()

    cvs_mean = np.mean(cvs)
    cvs_cv = variation(cvs)
    cvs_var = np.var(cvs)
    cvs_standard_deviation = np.std(cvs)
    print("average cvs", cvs_mean)
    print("variance cvs", cvs_var)
    print("standard deviation cvs", cvs_standard_deviation)
    print("coefficient of variation cvs", cvs_cv)

    supports_mean = np.mean(supports)
    supports_standard_deviation = np.std(supports)
    print("support mean", supports_mean)
    print("support standard deviation", supports_standard_deviation)
    print(supports)
    print("size of support", len(supports))

    print(support_neurons)
    print("Number of support neurons", len(support_neurons))
    print(support_source)

if __name__ == '__main__':
    generate_latency_plots()
    analyze_amplitudes()
