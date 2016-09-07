import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.pylab import rcParams
from matplotlib import rc
import seaborn as sb

# GRAPHICS SETUP:
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
rc('text', usetex=False)
fontSize = 16
sb.set_style('dark')
rcParams['ytick.labelsize'] = fontSize
rcParams['xtick.labelsize'] = fontSize


def GetDataDicts(fp):
    with nc.Dataset(fp) as ds:
        l3bVars = ds.groups['level-3_binned_data'].variables
        binlist = l3bVars['BinList'][:]
        wts = binlist['weights']
        bands = ['412', '443', '490', '510', '555', '670', '765', '865']
        rhoDict = {}
        rhoUncDict = {}
        rhotDict = {}
        for band in bands:
            rhoDict[band] = np.pi * l3bVars['Rrs_%s' % band][:]['sum'] / wts
            rhoUncDict[band] = (np.pi * l3bVars['Rrs_unc_%s' % band][:]['sum']
                                / wts)
            rhotDict[band] = l3bVars['rhot_%s' % band][:]['sum'] / wts
    return rhoDict, rhoUncDict, rhotDict


def GetPtileDict(dataDict, ptile=.95, bands=['412', '443', '490',
                                             '510', '555', '670']):
    dataPtileDict = dict.fromkeys(bands)
    for band in bands:
        sortedData = np.sort(dataDict[band])
        dataPtileDict[band] = sortedData[int(np.floor(sortedData.size *
                                                      ptile))]
    return dataPtileDict


def SummaryPlot(df, **kwargs):
    ptile = kwargs.pop("ptile", 0.95)
    bands = kwargs.pop("bands", ['412', '443', '490', '510', '555', '670'])
    colors = kwargs.pop("colors", ['black', 'brown', 'blue', 'm', 'c',
                                   'orange', 'r'])
    savepath = kwargs.pop('savepath', None)
    title = kwargs.pop('title', None)
    f, ax = pl.subplots(figsize=(12, 7))
    axYmaxBase = kwargs.pop('ymaxBase', 0.002)
    axYmax = kwargs.pop('ymax', axYmaxBase)
    axInYmax = 2.1e-4
    ax.set_ylim(0, axYmax)
    gboxY = 8e-5 / axYmax
    gboxY2 = 8e-5 / axInYmax
    ymaxScl = axYmaxBase / axYmax
    ax.set_xlim(412, 700)
    ax.set_xticks([412, 443, 490, 510, 555, 670])
    if title:
        ax.set_title(title, fontsize=22)
    ax.set_ylabel(r'uncertainty ($\rho$)', fontsize=17)
    ax.set_xlabel(r'$\lambda$', fontsize=18)
    ax.axvspan(412, 600, ymin=0, ymax=.5*ymaxScl, facecolor='gray', alpha=0.1)
    ax.axvspan(412, 600, ymax=.4*ymaxScl, facecolor='gray', alpha=0.3)
    ax.axvspan(600, 700, ymax=1 * ymaxScl,
               facecolor='gray', alpha=0.1, label='threshold')
    ax.axvspan(600, 700, ymax=.8 * ymaxScl, facecolor='gray', alpha=0.3,
               label='20% margin')
    ax.axvspan(650, 700, ymax=gboxY, facecolor='gold', alpha=0.4,
               label='nflh ROI')
    expList = df.columns.tolist()
    for exp, col in zip(expList, colors):
        lbl = '%s' % exp
        ax.plot(df[exp], label=lbl, marker='o', color=col, lw=1.5)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 3))
    ax.legend(loc='best', fontsize=18)
    if savepath:
        fmt = savepath.split('.')[-1] if '.' in savepath else 'png'
        f.savefig(savepath, dpi=300, format=fmt)
