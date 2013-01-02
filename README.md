TimeLapse
=========
Utility to create a time lapse movie from a series of images.

Platform Support
----------------
Currently only Windows is supported.  Mac support is in progress.

Usage
-----
 1. Run CreateTimeLapse.bat.
 2. Click the "Select Images" button to select the images to use.
 3. _(optional)_ Choose a frame rate.  Note that the video encoding has trouble below 10 frames-per-second.
 4. _(optional)_ Choose the video resolution.  If none is specified, the image resolution is used.
 5. Click the "Create Video From Images" button.
 6. View the created movie in the input-image directory. 

Dependencies
------------
##### Bundled with TimeLapse:
 * Python 3
 * mencoder (Part of the mplayer suite: www.mplayerhq.hu)

##### Not Bundled
 * cx_Freeze (http://cx-freeze.sourceforge.net/)

Create Standalone Executable
----------------------------
 1. Install cx_Freeze (http://cx-freeze.sourceforge.net/).
 2. Update CreateExecutable.py with the path to your python installation directory.
 3. Run ```CreateExecutable.py build.```.
 4. The output will be under ```./build/```.
 5. Optionally zip the output up and send to users.

Author
------
Harrison Ting
