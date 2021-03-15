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
        channel = filePath.channel
        if int(channel)==0:
            channel=0
        if filePath.downsample:
            reslevel = str(filePath.downsample)
        elif not filePath.downsample:
            reslevel=0
        filePath = filePath.file
    name, ext = os.path.splitext(filePath)
    if ext != '.ims':
        raise TypeError('Input filePath must be .ims file')   
    if name.endswith('.ome'):
        name = name.strip('.ome')
        ext = '.ome.ims'
    file = h5py.File(filePath, 'a')
    im = file.get('DataSet')
    if str(reslevel) != '0':
        print("Retrieving downsampled data at resolution level " + str(reslevel))
    res0 = im.get('ResolutionLevel ' + str(reslevel))
    time0 = res0.get('TimePoint 0')
    if len(list(time0.keys()))>1:
        if channel is not None:
            print("Multiple channels detected. Proceeding with channel " + str(channel))
        elif not channel:
            channel = input("Multiple channels detected but no --channel argument given. Input channel to process: ")
    fluo = time0.get('Channel ' + str(channel))
    stack = fluo.get('Data')
    if save:
        if not reslevel:        
            print("Converting " + name + " channel" + str(channel) + " from .ims to .tif")
            if not channel:
                imsave(name + '_C0.tif', np.array(stack), bigtiff=True)
            elif channel:
                imsave(name + "_C" + str(channel) + '.tif', np.array(stack), bigtiff=True)
            print('Completed at ' + str(time.ctime()))
        elif reslevel:
            print("Converting " + name + " channel" + str(channel) + " from .ims to .tif. Downsampled at res level " + str(reslevel))
            if not channel:
                imsave(name + '_C0_ResLevel' + str(reslevel) + '.tif', np.array(stack), bigtiff=True)
            elif channel:
                imsave(name + "_C" + str(channel) + '_ResLevel' + str(reslevel) + '.tif', np.array(stack), bigtiff=True)
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


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--file',type=str,default=os.getcwd())
    p.add_argument('--save',type=bool,default=True)
    p.add_argument('--channel',type=str,default=None)
    p.add_argument('--downsample',type=int,default=None)
    p.add_argument('--directory',type=str,default=None)
    p.add_argument('--nthreads',type=int,default=8)
    args = p.parse_args()
    if args.directory == None:
        IMStoTIF(args)
    elif args.directory:
        multiprocessIMStoTIF(args)