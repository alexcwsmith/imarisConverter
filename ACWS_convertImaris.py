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
        if filePath.channel:
            channel = filePath.channel
            if isinstance(channel, str):
                channel = int(channel)
        elif not filePath.channel:
            channel=0
        if filePath.downsample:
            reslevel = str(filePath.downsample)
        elif not filePath.downsample:
            reslevel=0
        pad = int(filePath.pad)
        filePath = filePath.file
    name, ext = os.path.splitext(filePath)
    if ext != '.ims':
        raise TypeError('Input filePath must be .ims file')
    if name.endswith('.ome'):
        name = name.strip('.ome')
        ext = '.ome.ims'
    file = h5py.File(filePath, 'r')
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
    if reslevel:
        raw = im.get('ResolutionLevel 0')
        rawt = raw.get('TimePoint 0')
        rawf = rawt.get('Channel 0')
        rawshape = rawf.get('Data').shape
        array = np.array(stack)
        array_mid = array[int(array.shape[0]/2),int(array.shape[1]/2),:int(array.shape[2]/2)]
        array_min = (array-int(array_mid.min())).astype(np.int16)
        array_min[array_min<0]=0
        array_min=array_min.astype(np.uint16)
        bounds = np.nonzero(array_min)
        minz = bounds[0].min()
        maxz = bounds[0].max()
        miny = bounds[1].min()
        maxy = bounds[1].max()
        minx = bounds[2].min()
        maxx = bounds[2].max()
        if miny-pad<0:
            miny = miny+pad
        if minx-pad<0:
            minx = minx+pad
        array_crop = array[minz:maxz, int(miny-pad):int(maxy+pad), int(minx-pad):int(maxx+pad)]
        print("Downsampled image data from original " + str(rawshape) + " to " + str(array_crop.shape))
    if save:
        print("Converting " + name + " channel " + str(channel) + " from .ims to .tif")
        if not reslevel:        
            if not channel:
                imsave(name + '_C0.tif', np.array(stack), check_contrast=False, bigtiff=True)
            elif channel:
                imsave(name + "_C" + str(channel) + '.tif', np.array(stack), check_contrast=False, bigtiff=True)
            print('Completed at ' + str(time.ctime()))
        elif reslevel:
            if not channel:
                imsave(name + '_C0_ResLevel' + str(reslevel) + '.tif', array_crop, check_contrast=False, bigtiff=True)
            elif channel:
                imsave(name + "_C" + str(channel) + '_ResLevel' + str(reslevel) + '.tif', array_crop, check_contrast=False, bigtiff=True)
            print('Completed at ' + str(time.ctime()))
    elif not save:
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
    p.add_argument('--file',type=str,default=os.getcwd(),help='Path to .ims file')
    p.add_argument('--channel',type=int,default=None,help='If a multiple-channel .ims file, specify 0-indexed channel number to extract. Default None')
    p.add_argument('--downsample',type=int,default=None,help='Downsampling factor for data extraction. Default None.')
    p.add_argument('--pad',type=int,default=0,help='Amount to pad downsampled images in XY dims, in pixels. Default 0.')
    p.add_argument('--directory',type=str,default=None,help='If you want to convert all .ims files in a directory, specify path to directory here')
    p.add_argument('--nthreads',type=int,default=8,help='Number of threads for multiprocessing when using --directory flag. \
                   This will be the number of files that are processed at once. \
                       Beware of the memory footprint of each thread, especially if not downsampling.')
    p.add_argument('--save',type=bool,default=True,help='Whether to save or return result. Default True to save image. Set False to return array for further processing.')
    args = p.parse_args()
    if args.directory == None:
        IMStoTIF(args)
    elif args.directory:
        multiprocessIMStoTIF(args)