# imarisConverter
Convert .ims to .tif files, either one at a time, or for an entire directory.

There are three primary modes to use this:

* Convert & save single file (command line):
```
python3 ACWS_convertImaris.py --file=yourFileName --save=true
```
If your .ims files have multiple channels, there is also an optional --channels parameter.
It's worth nothing that this is 0-indexed, whereas I believe Imaris is 1-indexed. So channels 1 & 2 in imaris would be 0 & 1 here.
```
python3 ACWS_convertImaris.py --file=yourFileName --save=true --channel=0
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
from skimage.io import imsave
imsave('pathToSaveFileTo.tif', im_medfilt, bigtiff=True)
```

For full clarity, here's an example converting all .ims files in a directory with multiprocessing: 
<img width="1440" alt="ConvertWholeDirectory" src="https://user-images.githubusercontent.com/47009665/111088221-813fd000-84fc-11eb-9731-aabd4825cfcf.png">


Feel free to file issues with any bugs, or email me directly. Pull requests also welcome for additional features!
