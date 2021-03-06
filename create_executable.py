"""
Creates a standalone executable of the program.
"""
import os
import sys

import cx_Freeze


USE_CONSOLE = False
VERSION = '0.1'

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if not USE_CONSOLE and sys.platform == "win32":
    base = "Win32GUI"

sys.path.append(os.path.realpath('Source'))

cx_Freeze.setup(
    name='TimeLapse',
    version=VERSION,
    description='Creates a movie from a series of images.',
    url='https://github.com/harrisont/TimeLapse',
    options={
        'build_exe': {
            'compressed': True,
            'include_msvcr': True,
            'create_shared_zip': False,
            'includes': [
                'Mencoder',
                'ImageHelper',
                'Log',
                'PlatformHelper',
                'TkinterWidgets',
            ],
            'include_files': [
                'External/mplayer/',
                'Resources/radian.ico',
            ],
            'constants': [
                'rootRelativePath=".."',
            ],
        }
    },
    executables=[
        cx_Freeze.Executable(
            script='Source/create_time_lapse.py',
            targetName='TimeLapse.exe',
            base=base,
            icon='Resources/radian.ico',
            copyDependentFiles=True,
            appendScriptToExe=True,
        ),
    ])
