import scipy.optimize
import numpy as np
import pickle
import os
import matplotlib.pyplot as pl

bands = ['412', '443', '490', '510', '555', '670']
simDirDict = {k: 'NIR_SNR_' + str(k) for k in range(500, 850, 50)}
fontSize = 16


def GetXFor95(nirSnrDir, rhotDict, rhoUncDict):
    global data
    global uncData
    Xfor95_path = '/accounts/ekarakoy/UNCERTAINTIES/datafiles/XBiasFor95.p'
    if os.path.exists(Xfor95_path):
        Xfor95Dict = pickle.load(open(Xfor95_path, 'rb'))
    else:
        Xfor95Dict = dict.fromkeys(simDirDict.values())
    Xfor95Dict[nirSnrDir] = dict.fromkeys(bands[:-2])
    for band in bands[:-2]:
        data = rhotDict[band]
        uncData = rhoUncDict[band]
        rngs = slice(0, 5, 0.25)
        x_targ = scipy.optimize.brute(FindBiasPercdata, (rngs,))
        print("%s: %s: %.3f" % (nirSnrDir, band, x_targ))
        Xfor95Dict[nirSnrDir][band] = x_targ
    pickle.dump(Xfor95Dict, open(Xfor95_path, 'wb'))


def FindBiasPercdata(x):
    global data
    global uncData
    thresh = 0.001
    targData = np.sqrt(np.power(uncData, 2) + np.power((x/100)*data, 2))
    sortedData = np.sort(targData)
    rho95 = sortedData[int(np.floor(sortedData.size * .95))]
    result = abs(rho95 - thresh)
    return result


def PlotArtifacts(dataDict, artNoiseX, **kwargs):
    rng = kwargs.pop("rnge", (0, 6e-3))
    colors = kwargs.pop("colors", ['black', 'indigo', 'blue', 'green'])
    savename = kwargs.pop("savename", None)
    band = kwargs.pop("band", '412')
    snr = kwargs.pop("snr", '500')
    f, ax = pl.subplots(figsize=(10, 6))
    rhoThresh = 0.001
    f.suptitle(r'$\lambda=%s$ ABS. UNC. w/ NIR SNR=%s ' % (band, snr),
               fontsize=18)
    firstPass = True
    for col, xsi in zip(colors, artNoiseX):
        lbl0 = float(xsi) * 100
        lbl = r'bias (%%$\rho_t$) : %.1f' % lbl0
        data = dataDict[band][xsi]
        sortedData = np.sort(data)
        rho95 = sortedData[int(np.floor(sortedData.size * .95))]
        pOK = data[data <= rhoThresh].size / data.size * 100
        lbl += r'$\rightarrow$ %.2f%% OK' % pOK
        if firstPass:
            ax.axvspan(0, rhoThresh, color='orange', alpha=0.2,
                       label='threshold')
            firstPass = False
            ax.axvline(x=rho95, color=col, label="95%", linestyle='--')
        else:
            ax.axvline(x=rho95, color=col, linestyle='--')
        ax.hist(data, bins=100, range=rng, histtype='stepfilled', color=col,
                alpha=0.65, normed=True, label=lbl)

        # ax.set_title(r'$\sigma_{\rho_w}$ (art. unc: %s)' % xsi)
    ax.legend(loc='best', fontsize=fontSize-3)
    ax.set_xlabel(r'$ \rho_w$ inc. added bias as % $\rho_t$',
                  fontsize=fontSize)
    ax.set_ylabel('Freq.', fontsize=fontSize)
    ax.ticklabel_format(axis='both', style='sci', scilimits=(1, 3))
    if savename:
        f.savefig(savename, dpi=300, format='png')


def CalcRhoW(data, uncData, x):
    targData = np.sqrt(np.power(uncData, 2) + np.power((x/100)*data, 2))
    sortedData = np.sort(targData)
    rho95 = sortedData[int(np.floor(sortedData.size * .95))]
    print(rho95)


def Get95Ptiles(biasList, dataDict):
    rho95Dict = dict.fromkeys(bands[:-2])
    for band in bands[:-2]:
        rho95Dict[band] = dict.fromkeys(biasList)
        for bias in biasList:
            data = dataDict[band][bias]
            sortedData = np.sort(data)
            rho95Dict[band][bias] = sortedData[int(np.floor(sortedData.size *
                                                            .95))]
    return rho95Dict
