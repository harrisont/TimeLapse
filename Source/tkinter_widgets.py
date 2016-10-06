import doctest
import logging
import tkinter as tk
from tkinter import ttk


logger = logging.getLogger(__name__)


class Label(ttk.Label):
    """Overrides ttk.Label to provide convenience methods."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def disable(self):
        self.state(['disabled'])

    def enable(self):
        self.state(['!disabled'])


class Entry(ttk.Entry):
    """Overrides ttk.Entry to provide convenience methods.

    If the optional keyword argument 'changed_command' is set to a function,
    that function will be called whenever the entry's value changes.

    Subclasses can override _is_text_valid to provide their own validation.
    """
    def __init__(self, parent, **kwargs):
        self.text_var = tk.StringVar()

        # If changed_command exists, call it on changes, ignoring the default trace parameters.
        if 'changed_command' in kwargs:
            command = kwargs['changed_command']
            self.text_var.trace('w', lambda var_name, index, operation: command())
            del kwargs['changed_command']

        super().__init__(
            parent,
            textvariable=self.text_var,
            **kwargs)

        # Bind Control-a to select-all (the default is Control-/).
        self.bind('<Control-a>', self.handle_select_all_event)

        is_valid_command = self.register(self._is_text_valid)
        self.config(validate='all', validatecommand=(is_valid_command, '%P'))

    def get_text(self):
        return self.text_var.get()

    def is_empty(self):
        return len(self.get_text()) == 0

    def clear_text(self):
        self.set_text('')

    def set_text(self, text):
        self.text_var.set(text)

    def disable(self):
        self.state(['disabled'])

    def enable(self):
        self.state(['!disabled'])

    @staticmethod
    def handle_select_all_event(event):
        event.widget.select_range(0, tk.END)
        return 'break'

    def _is_text_valid(self, text):
        return True


class IntegerEntry(Entry):
    """Overrides Entry to validate that the text is an integer."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def is_valid(self):
        return self._is_text_valid(self.get())

    @staticmethod
    def _is_text_valid(text):
        """
        >>> IntegerEntry._is_text_valid('123')
        True

        >>> IntegerEntry._is_text_valid('')
        True

        >>> IntegerEntry._is_text_valid('1.5')
        False

        >>> IntegerEntry._is_text_valid('-2')
        True

        >>> IntegerEntry._is_text_valid(' ')
        False

        >>> IntegerEntry._is_text_valid('a')
        False

        >>> IntegerEntry._is_text_valid('1a')
        False
        """
        try:
            if text:
                int(text)
            return True
        except ValueError:
            logger.debug('Invalid text entry "{}"'.format(text))
            return False


class LabelledEntryControl(ttk.Frame):
    """A frame with a label and an entry to the right of it."""

    def __init__(self, parent, label_text, **kwargs):
        """Uses Tkinter.Entry by default.  Pass in a value for 'entry_class' to use a different entry class."""

        self.enable_entry_when_control_enabled = True

        entry_class = Entry
        if 'entry_class' in kwargs:
            entry_class = kwargs['entry_class']
            del kwargs['entry_class']

        label_keyword_args = {}
        if 'label_args' in kwargs:
            label_keyword_args = kwargs['label_args']
            del kwargs['label_args']

        entry_keyword_args = {}
        if 'entry_args' in kwargs:
            entry_keyword_args = kwargs['entry_args']
            del kwargs['entry_args']

        super().__init__(parent, **kwargs)

        self.label = Label(self, text=label_text, **label_keyword_args)
        self.label.pack(side=tk.LEFT)

        self.entry = entry_class(self, **entry_keyword_args)
        self.entry.pack(side=tk.RIGHT)

    def get_text(self):
        return self.entry.get_text()

    def is_empty(self):
        return self.entry.is_empty()

    def clear_text(self):
        self.entry.clear_text()

    def set_text(self, text):
        # Text can only be set when the entry is enabled.
        if self.is_entry_enabled():
            self.entry.set_text(text)
        else:
            self.entry.enable()
            self.entry.set_text(text)
            self.entry.disable()

    def disable(self):
        self.disable_label()
        self.entry.disable()

    def enable(self):
        self.enable_label()
        if self.enable_entry_when_control_enabled:
            self.entry.enable()

    def is_entry_enabled(self):
        return self.entry.instate(['!disabled'])

    def disable_entry(self):
        self.enable_entry_when_control_enabled = False
        self.entry.disable()

    def enable_entry(self):
        self.enable_entry_when_control_enabled = True
        self.entry.enable()

    def disable_label(self):
        self.label.disable()

    def enable_label(self):
        self.label.enable()


class CheckboxControl(ttk.Checkbutton):
    """Convenience wrapper around ttk.Checkbutton."""

    def __init__(self, parent, text, **kwargs):
        self.checkbox_value_var = tk.IntVar()

        # We don't want to trigger command when we call invoke (see below),
        # so we don't set command until after calling invoke.
        command = None
        if 'command' in kwargs:
            command = kwargs['command']
            del kwargs['command']

        super().__init__(
            parent,
            variable=self.checkbox_value_var,
            text=text,
            **kwargs)

        # Need to call invoke twice to initialize the unchecked state.
        self.invoke()
        self.invoke()

        if command:
            self.config(command=command)

    def is_checked(self):
        return self.checkbox_value_var.get() == 1

    def check(self):
        self.set_checked(True)

    def uncheck(self):
        self.set_checked(False)

    def set_checked(self, is_checked):
        if is_checked:
            value = 1
        else:
            value = 0
        self.checkbox_value_var.set(value)

    def disable(self):
        self.state(['disabled'])

    def enable(self):
        self.state(['!disabled'])


class ImageScaleControl(ttk.LabelFrame):
    """A frame with two LabelledEntryControl's for width and height."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text='Image Size', **kwargs)

        frame = ttk.Frame(self)

        self.aspect_ratio = 1
        self.validity_changed_callback = None

        self.keep_aspect_ratio_control = CheckboxControl(
            frame,
            'Maintain Aspect Ratio',
            command=self._changed_keep_aspect_ratio)
        self.keep_aspect_ratio_control.pack()

        self.width_control = LabelledEntryControl(
            frame,
            'Width',
            entry_class=IntegerEntry,
            entry_args={'changed_command': self._changed_width})
        self.width_control.pack(fill=tk.X, padx=4, pady=1)

        self.height_control = LabelledEntryControl(
            frame,
            'Height',
            entry_class=IntegerEntry,
            entry_args={'changed_command': self._changed_height})
        self.height_control.pack(fill=tk.X, padx=4, pady=1)

        self.cached_is_valid = self.is_valid()

        self.set_keep_aspect_ratio(True)
        # The checked-event doesn't trigger while initializing, so trigger it manually.
        self._changed_keep_aspect_ratio()

        frame.pack(pady=(0, 4))

    def get_keep_aspect_ratio(self):
        return self.keep_aspect_ratio_control.is_checked()

    def set_keep_aspect_ratio(self, should_keep_aspect_ratio):
        self.keep_aspect_ratio_control.set_checked(should_keep_aspect_ratio)

    def _changed_keep_aspect_ratio(self):
        if self.get_keep_aspect_ratio():
            self._set_height_from_aspect_ratio_corrected_height()
            self.height_control.disable_entry()
        else:
            self.height_control.enable_entry()

    def _changed_width(self):
        if self.get_keep_aspect_ratio():
            self._set_height_from_aspect_ratio_corrected_height()
        self._update_validity()

    def _changed_height(self):
        self._update_validity()

    def _update_validity(self):
        new_is_valid = self.is_valid()
        if new_is_valid != self.cached_is_valid:
            self.cached_is_valid = new_is_valid
            if self.validity_changed_callback:
                self.validity_changed_callback()

    def get_aspect_ratio(self):
        return self.aspect_ratio

    def get_width(self):
        return int(self.width_control.get_text())

    def get_height(self):
        return int(self.height_control.get_text())

    def get_width_and_height(self):
        return self.get_width(), self.get_height()

    def set_width(self, width):
        self._set_width_with_no_aspect_ratio_correction(width)
        if self.get_keep_aspect_ratio():
            self._set_height_from_aspect_ratio_corrected_height()

    def set_height(self, height):
        self._set_height_with_no_aspect_ratio_correction(height)
        if self.get_keep_aspect_ratio():
            self._set_width_from_aspect_ratio_corrected_height()

    def set_width_and_height(self, width, height):
        self.aspect_ratio = width / height
        self._set_width_with_no_aspect_ratio_correction(width)
        self._set_height_with_no_aspect_ratio_correction(height)

    def _set_width_with_no_aspect_ratio_correction(self, width):
        self.width_control.set_text(round(width))

    def _set_height_with_no_aspect_ratio_correction(self, height):
        self.height_control.set_text(round(height))

    def _set_width_from_aspect_ratio_corrected_height(self):
        try:
            height = self.get_height()
        except ValueError:
            self.width_control.clear_text()
            return
        self._set_width_with_no_aspect_ratio_correction(height * self.get_aspect_ratio())

    def _set_height_from_aspect_ratio_corrected_height(self):
        try:
            width = self.get_width()
        except ValueError:
            self.height_control.clear_text()
            return
        self._set_height_with_no_aspect_ratio_correction(width / self.get_aspect_ratio())

    def is_valid(self):
        return self.width_control.entry.is_valid() \
            and self.height_control.entry.is_valid() \
            and not self.width_control.is_empty() \
            and not self.height_control.is_empty()

    def set_validity_changed_callback(self, callback):
        self.validity_changed_callback = callback

    def disable(self):
        self.keep_aspect_ratio_control.disable()
        self.width_control.disable()
        self.height_control.disable()

    def enable(self):
        self.keep_aspect_ratio_control.enable()
        self.width_control.enable()
        if not self.get_keep_aspect_ratio():
            self.height_control.enable()

if __name__ == '__main__':
    doctest.testmod()
