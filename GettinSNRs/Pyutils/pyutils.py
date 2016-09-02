import pickle
import pandas
import os

cfDictPath= '/accounts/ekarakoy/UNCERTAINTIES/datafiles/cfDict.p'
coefDict = pickle.load(open(cfDictPath,"rb"))
parfilePath = '/accounts/ekarakoy/UNCERTAINTIES/parfiles/PACE/'

def SWF2PACEFacs(idstr,dataFrame,verbose=True):
    "Return noise scale factors from SWF to PACE for given SNR set"
    
    bands=[412,443,490,510,555,665,748,865]
    ltyps=dict.fromkeys(bands)
    targSnr = dict.fromkeys(bands)
    targSnr=dict(dataFrame.loc[bands,idstr])
    ltyps = dict(dataFrame.loc[bands].Ltyp)
    if verbose:
        print(targSnr)
    targFac=dict.fromkeys(bands)
    for i,band in enumerate(bands):
        if band == 665:
            cband = '670'
        elif band == 748:
            cband ='765'
        else:
            cband = str(band)
        oldsnr=ApplyPolyFit(coefDict[cband],ltyps[band])
        targFac[band] = targSnr[band]/oldsnr
        if verbose:
            print("%s=>old snr: %f - fac(target): %f" % (band,oldsnr,targFac[band]))
    return targFac
    

def ApplyPolyFit(cf,lt,deg=4):
    y = 0
    for i in range(deg):
        y += cf[i] * (lt** (deg - i))
    y += cf[deg]
    return y
    

def WriteParfile(idstr,bands,targFac,path=parfilePath):
    """ writes parfile for given noise scale factors"""
    fname='parfile_noisy_%s' % idstr
    fpath = os.path.join(path,fname)
    nsList = '['
    for band in bands:
        band = int(band)  
        if band == '-1':
            nsList += '%s' % band
        else:
            if band == 670:
                band = 665
            elif band == 765:
                band = 748
            nsList+='%.6f' % targFac[band]
        if band != int(bands[-1]):
            nsList +=','
    nsList +=']'
    prods = '"Rrs_nnn,a_nnn_qaa,b_nnn_qaa,Lt_nnn,chlor_a,rhot_nnn"'
    with open(fpath,'w') as f:
        f.write('l2prod=%s\n' % prods)
        f.write('add_noise_sigma=1\n')
        f.write('noise_scale= %s\n' % str(nsList) )
        f.write('oformat=netcdf4')    
