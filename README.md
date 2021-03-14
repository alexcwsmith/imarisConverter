# imarisConverter
Convert .ims to .tif files, either one at a time, or full an entire directory.

There are three primary modes to use this:

* Convert & save single file (command line):
```
python3 ACWS_convertImaris.py --file=yourFileName --save=true
```
* Convert & save all files in directory (command line; be careful of memory of each thread):
```
python3 ACWS_convertImaris.py --directory=pathToDirectory --nthreads=12
```
* Convert single file & return array for further processing (in an ipython console, IDE, or jupyter notebook):
```
import ACWS_convertImaris as conv
im = conv.IMStoTIF('yourFilePathHere', save=False)
#example now process with a medial filter:
from scipy.signal import medfilt
im_medfilt = medfilt(im, kernel_size=3)
from skimage.io import imsave
imsave('pathToSaveFileTo.tif', im_medilt, bigtiff=True)
```
Feel free to file issues with any bugs, or email me directly. Pull requests also welcome for additional features!
