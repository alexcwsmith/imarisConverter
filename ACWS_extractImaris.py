#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 20:30:15 2021

@author: smith
"""


import os
from skimage.io import imsave
import numpy as np
import h5py
from pathos.pools import ProcessPool
import argparse
import time
        
def _multiSaveIMS(plane, imsFile, channel):
    file = h5py.File(imsFile, 'r')
    name = os.path.basename(imsFile)
    n, e = os.path.splitext(name)
    imNumPadded = str(plane).zfill(4)
    directory = os.path.dirname(imsFile)
    data = file.get('DataSet/ResolutionLevel 0/TimePoint 0/Channel ' + str(channel)+'/Data')
    imsave(os.path.join(directory, n + '_C'+str(channel)+'/' + n + '_C' + str(channel) + '_Z' + imNumPadded + '.tif'), np.array(data[plane]), check_contrast=False)
  
def multiSaveIMS(imsFile, channel, nthreads):
    name = os.path.basename(imsFile)
    n, e = os.path.splitext(name)
    directory = os.path.dirname(imsFile)
    if not os.path.exists(os.path.join(directory, n + '_C' + str(channel)+'/')):
        os.mkdir(os.path.join(directory, n + '_C' + str(channel)+'/'))
    print("Started at " + time.ctime())
    file = h5py.File(imsFile, 'r')
    data = file.get('DataSet/ResolutionLevel 0/TimePoint 0/Channel ' + str(channel) + '/Data')
    print("Loaded data of shape " + str(data.shape))
    planes = list(range(data.shape[0]))
    pool = ProcessPool(nodes=nthreads)
    pool.map(_multiSaveIMS, list(planes), list([imsFile]*len(planes)), list([channel]*len(planes)))
    pool.close()
    pool.join()
    print("Finished at " + time.ctime())

if __name__ == '__main__':    
    p = argparse.ArgumentParser()
    p.add_argument('--file',type=str,help='Path to .ims file')
    p.add_argument('--channel',type=int,default=0,help='If a multiple-channel .ims file, specify 0-indexed channel number to extract. Default None')
    p.add_argument('--nthreads',type=int,default=24,help='Number of threads for multiprocessing.')
    args = p.parse_args()
    multiSaveIMS(args.file, args.channel, args.nthreads)