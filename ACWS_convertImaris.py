#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 16:35:16 2021

@author: smith
"""

import os
import h5py
import numpy as np
from skimage.io import imsave
import argparse
import time
from pathos.pools import ProcessPool


def IMStoTIF(filePath, save=True):
    print("Started at " + str(time.ctime()))
    if isinstance(filePath, argparse.Namespace):
        save = filePath.save
        filePath = filePath.file
        print("Running on file" + filePath)
    name, ext = os.path.splitext(filePath)
    if ext != '.ims':
        raise TypeError('Input filePath must be .ims file')      
    file = h5py.File(filePath, 'a')
    im = file.get('DataSet')
    res0 = im.get('ResolutionLevel 0')
    time0 = res0.get('TimePoint 0')
    auto = time0.get('Channel 0')
    stack = auto.get('Data')
    if save:
        print("Converting & Saving " + name + ".tif")
        imsave(name + '.tif', np.array(stack), bigtiff=True)
        print('Completed at ' + str(time.ctime()))
    if not save:
        return(np.array(stack))

def _IMStoTIF(filePath):
    name, ext = os.path.splitext(filePath)
    if ext != '.ims':
        raise TypeError('Input filePath must be .ims file')      
    file = h5py.File(filePath, 'a')
    im = file.get('DataSet')
    res0 = im.get('ResolutionLevel 0')
    data = res0.get('TimePoint 0')
    auto = data.get('Channel 0')
    stack = auto.get('Data')
    print("Converting & Saving " + name + ".tif")
    imsave(name + '.tif', np.array(stack), bigtiff=True)

def multiprocessIMStoTIF(args):
    print("Starting at " + str(time.ctime()))
    processes = int(args.nthreads)
    files = os.listdir(str(args.directory))
    queue = []
    for f in files:
        name, ext = os.path.splitext(f)
        if f.endswith('.ims'):
            if not os.path.exists(name + '.tif'):
                queue.append(f)
    if len(queue)==0:
        print("No unprocessed files in directory.")
        return(files)
    os.chdir(str(args.directory))
    pool = ProcessPool(nodes=processes)
    pool.map(_IMStoTIF, queue)
    pool.close()
    pool.join()
    print('Completed at ' + str(time.ctime()))


if __name__ =='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--file',type=str,default=os.getcwd())
    p.add_argument('--save',type=bool,default=True)
    p.add_argument('--directory',type=str,default=None)
    p.add_argument('--nthreads',type=int,default=8)
    args = p.parse_args()
    if args.directory == None:
        IMStoTIF(args)
    elif args.directory:
        multiprocessIMStoTIF(args)