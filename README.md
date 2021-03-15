# imarisConverter
Convert .ims to .tif files, either one at a time, or for an entire directory.

There are three modes to use this:

* Convert & save single file (command line):
Usage for the simplest use case, for a .ims file with only one channel. This takes ~2 minutes for a 20GB .ims file on my system.
```
python3 ACWS_convertImaris.py --file=yourFileName
```
There are also several optional arguments you can pass. You can see all of them with:
```
python3 ACWS_convertImaris.py --help
```
Which will print:
```
usage: ACWS_convertImaris.py [-h] [--file FILE] [--save SAVE]
                             [--channel CHANNEL] [--downsample DOWNSAMPLE]
                             [--directory DIRECTORY] [--nthreads NTHREADS]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           Specify path to .ims file
  --save SAVE           Specify whether to save or return result. Default True
  --channel CHANNEL     If a multiple-channel .ims file, specify 0-indexed
                        channel number to extract. Default None
  --downsample DOWNSAMPLE
                        Downsampling factor for data extraction. Default None.
  --directory DIRECTORY
                        If you want to convert all .ims files in a directory,
                        specify path to directory here
  --nthreads NTHREADS   Number of threads for multiprocessing when using
                        --directory flag. This will be the number of files
                        that are processed at once. Beware of the memory
                        footprint of each thread!

```
It's worth nothing that everything here is 0-indexed, whereas I believe Imaris is 1-indexed. So channels 1 & 2 in imaris would be 0 & 1 here, respectively.

The range of options for downsampling for my Imaris files is 0-5. This can be nice if you just want to get a quick view of your data in TIF format. Setting downsample=3 is approximately 10-fold downsampling (results in 256x256 images on my data), and this runs in 1 second.

For example, if you want to extract only the second channel, and downsample the data:
```
python3 ACWS_convertImaris.py --file=yourFileName --channel=1 --downsample=3
```

* Convert & save all files in directory (command line; be careful of memory footprint of each thread):
```
python3 ACWS_convertImaris.py --directory=pathToDirectory --nthreads=12
```
* Convert single file & return array for further processing (in an ipython console, IDE, or jupyter notebook):
```
import ACWS_convertImaris as conv
im = conv.IMStoTIF('yourFilePathHere', save=False)
#example now process with a median filter:
from scipy.signal import medfilt
im_medfilt = medfilt(im, kernel_size=3)
#save image with median filter
from skimage.io import imsave
imsave('pathToSaveFileTo.tif', im_medfilt, bigtiff=True)
```

For full clarity, here's an example converting all .ims files in a directory with multiprocessing: 
<img width="1440" alt="ConvertWholeDirectory" src="https://user-images.githubusercontent.com/47009665/111088221-813fd000-84fc-11eb-9731-aabd4825cfcf.png">


Feel free to file issues with any bugs, or email me directly. Pull requests also welcome for additional features!

#ToDo List:
* add functionality to extract multiple channels and save as a multi-channel .tif
* add optional in-line processing (minimum/median filters etc)
* Check if downsampling data here is a good option for generating LR/HR input images for GANfocal model.
