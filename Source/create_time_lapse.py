# Tkinter info:
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
import argparse
import doctest
import logging
import os
import pprint
import queue
import sys
import threading
import tkinter
from tkinter import ttk
import tkinter.filedialog

import directories
import image_helper
import mencoder
import platform_helper
import tkinter_widgets


logger = logging.getLogger(__name__)


class TimeLapseVideoFromImagesDialog(ttk.Frame):
    def __init__(self, window):
        ttk.Style().configure('Toplevel.TFrame', padx=5, pady=5)
        super().__init__(
            window,
            style='Toplevel.TFrame')

        ttk.Style().configure('TButton', padx=5, pady=5)

        window.wm_title("TimeLapse")
        window.iconbitmap(default=os.path.join(directories.get_resources_directory(), 'radian.ico'))

        self.window = window
        self.image_file_names = []
        self.create_movie_button = None
        self.images_list_control = None
        self.frames_per_second_control = None
        self.status_label = None
        self.image_scale_control = None
        self.result_queue = None
        self.mencoder_process = None

        self.init_select_images_button()
        self.init_images_list_control()
        self.init_frames_rate_control()
        self.init_image_scale_control()
        self.init_create_movie_button()
        self.init_status_control()

    def init_select_images_button(self):
        ttk.Button(
            self,
            text='Select Images',
            command=self.select_images,
            style='TButton'
            ).pack(fill=tkinter.X)

    def init_create_movie_button(self):
        self.create_movie_button = ttk.Button(
            self,
            text='Create Video From Images',
            command=self.create_movie,
            state=tkinter.DISABLED,
            style='TButton')
        self.create_movie_button.pack(
            fill=tkinter.X,
            pady=4)

    def _set_create_movie_button_enabled(self, is_enabled):
        if is_enabled:
            button_state = tkinter.NORMAL
        else:
            button_state = tkinter.DISABLED
        self.create_movie_button.config(state=button_state)

    def init_images_list_control(self):
        # Setup a list-box and scroll bars for it.
        # See http://effbot.org/zone/tk-scrollbar-patterns.htm for scrollbar documentation.

        frame = ttk.Frame(
            self,
            borderwidth=2,
            relief=tkinter.SUNKEN)

        scrollbar_y = ttk.Scrollbar(frame)
        scrollbar_x = ttk.Scrollbar(frame, orient=tkinter.HORIZONTAL)
        scrollbar_y.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        scrollbar_x.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.images_list_control = tkinter.Listbox(
            frame,
            borderwidth=0,
            width=80,
            height=6,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set)
        self.images_list_control.pack(fill=tkinter.BOTH, expand=True)

        scrollbar_y.config(command=self.images_list_control.yview)
        scrollbar_x.config(command=self.images_list_control.xview)

        frame.pack(
            fill=tkinter.BOTH,
            expand=True,
            pady=(0, 4))

    def init_frames_rate_control(self):
        frame = ttk.Frame(self)

        ttk.Label(
            frame,
            text="Frames per second:").pack(side=tkinter.LEFT)

        frame_rate_var = tkinter.StringVar()
        frame_rate_var.set(24)
        self.frames_per_second_control = tkinter.Spinbox(
            frame,
            from_=10,
            to=60,
            increment=2,
            textvariable=frame_rate_var,
            width=4)
        self.frames_per_second_control.pack()

        frame.pack(pady=4)

    def init_status_control(self):
        self.status_label = ttk.Label(self)
        self.status_label.pack()

    def init_image_scale_control(self):
        self.image_scale_control = tkinter_widgets.ImageScaleControl(self)
        self.image_scale_control.set_validity_changed_callback(self._image_scale_control_validity_changed)
        self.image_scale_control.disable()
        self.image_scale_control.pack(pady=(0, 4))

    def set_status_label(self, text):
        self.status_label.config(text=text)

    def user_message(self, message):
        logger.info(message)
        self.set_status_label(message)

    def select_images(self):
        """Bring up a dialog to allow the user to select one or more images.
        Return a list of the selected image file names.
        """
        files = tkinter.filedialog.askopenfilenames(
            parent=self.window,
            title="Select Images",
            filetypes=[("Image", ".jpg"), ("Image", ".jpeg"), ("Image", ".png"), ("All Files", ".*")])
        if not files:
            return
        logger.debug("File picker returned \n{}.".format(pprint.pformat(files)))

        image_file_names = self.get_image_file_names(files)
        logger.debug("Settings images to \n{}".format(pprint.pformat(image_file_names)))

        self.set_status_label('')

        encoding, error_message = image_helper.get_image_encoding_from_file_names(image_file_names)
        if encoding == image_helper.ImageEncoding.unknown:
            self.user_message(error_message)
            image_file_names = []

        self.set_images(image_file_names)

    def get_image_file_names(self, files):
        """The file picker returns different types on different platforms.
        This handles each one.
        """
        platform = platform_helper.get_platform()
        if platform == platform_helper.Platforms.windows:
            # Windows returns a single string for the file list.
            return self.window.tk.splitlist(files)
        else:
            # Mac returns a tuple of files.
            # Also use this in the default case.
            return files

    def set_images(self, image_file_names):
        self.image_file_names = image_file_names

        self.images_list_control.delete(0, tkinter.END)
        self.images_list_control.insert(0, *image_file_names)

        if len(image_file_names) > 0:
            # Enable controls that are dependent on having selected images.
            self._set_create_movie_button_enabled(True)
            self.image_scale_control.enable()

            content_type, width, height = image_helper.get_image_info_from_image(image_file_names[0])
            self.image_scale_control.set_width_and_height(width, height)
        else:
            self._set_create_movie_button_enabled(False)

    def get_scaled_resolution(self):
        return self.image_scale_control.get_width_and_height()

    def validate_scaled_resolution(self):
        if self.image_scale_control.is_valid():
            return True
        else:
            self.user_message("Invalid image scaling.")
            return False

    def _image_scale_control_validity_changed(self):
        is_valid = self.image_scale_control.is_valid()
        self._set_create_movie_button_enabled(is_valid)

    def get_frames_per_second(self):
        return self.frames_per_second_control.get()

    def create_movie(self):
        """Use MEncoder to create a movie from the images.
        Run it as a separate process and start checking to see if it is running (asynchronously).
        """
        if not self.validate_scaled_resolution():
            return
        width, height = self.get_scaled_resolution()

        self.user_message("Creating movie...")

        resolution_str = '<image-size>'
        if width and height:
            resolution_str = '({}x{})'.format(width, height)

        logger.debug('Creating movie: images="{}", FPS=({}), resolution={}'.format(
            self.image_file_names,
            self.get_frames_per_second(),
            resolution_str))

        self.result_queue = queue.Queue()

        self.mencoder_process = threading.Thread(
            target=self.create_movie_and_store_result,
            args=(
                self.image_file_names,
                self.get_frames_per_second(),
                width,
                height))
        self.mencoder_process.start()
        self.check_if_mencoder_running()

    def create_movie_and_store_result(self, image_file_names, frames_per_second, width, height):
        """Wraps CreateMovie and stores the result in a Queue.
        """
        result = mencoder.create_movie_from_images(
            image_file_names,
            frames_per_second,
            width,
            height)
        self.result_queue.put(result)

    def check_if_mencoder_running(self):
        self.mencoder_process.join(0)
        if self.mencoder_process.is_alive():
            logger.debug('MEncoder is still running; rescheduling check.')
            self.schedule_mencoder_status_check()
        else:
            result = self.result_queue.get()
            self.mencoder_finished(result)

    def schedule_mencoder_status_check(self):
        mencoder_is_running_interval_milliseconds = 100
        self.after(mencoder_is_running_interval_milliseconds, self.check_if_mencoder_running)

    def mencoder_finished(self, result):
        if result:
            movie_path = result
            self.user_message("Created movie: {}".format(movie_path))
        else:
            self.user_message("Error in creating movie.")


def run_doc_tests():
    num_failures, num_tests = doctest.testmod()
    return num_failures == 0


def redirect_output_to_null():
    null = open(os.devnull, 'w')
    sys.stdout = null
    sys.stderr = null


def main():
    parser = argparse.ArgumentParser(description='Create time lapse movies from series of images.')
    parser.add_argument('--log-level', choices=['error', 'warning', 'info', 'debug'], default='info')
    args = parser.parse_args()

    numeric_log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(format='[%(name)s] %(levelname)s: %(message)s', level=numeric_log_level)

    if not sys.stdout:
        redirect_output_to_null()

    if not run_doc_tests():
        return

    window = tkinter.Tk()
    TimeLapseVideoFromImagesDialog(window).pack(
        fill=tkinter.BOTH,
        expand=True,
        padx=2,
        pady=2)

    # Update the window so that it calculates the size,
    # then use it to set the minimum size to prevent distortions
    # when users resize the window very small.
    window.update()
    window.minsize(window.winfo_width(), window.winfo_height())

    window.mainloop()

if __name__ == '__main__':
    main()
