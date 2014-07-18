"""Int class.  

Represents an unbounded int using a widget.
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2013, the IPython Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from .widget import DOMWidget
from IPython.utils.traitlets import Unicode, CInt, Bool, Enum
from IPython.utils.warn import DeprecatedClass

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------
class _Int(DOMWidget):
    value = CInt(0, help="Int value", sync=True) 
    disabled = Bool(False, help="Enable or disable user changes", sync=True)
    description = Unicode(help="Description of the value this widget represents", sync=True)


class _BoundedInt(_Int):
    step = CInt(1, help="Minimum step that the value can take (ignored by some views)", sync=True)
    max = CInt(100, help="Max value", sync=True)
    min = CInt(0, help="Min value", sync=True)

    def __init__(self, *pargs, **kwargs):
        """Constructor"""
        DOMWidget.__init__(self, *pargs, **kwargs)
        self.on_trait_change(self._validate, ['value', 'min', 'max'])

    def _validate(self, name, old, new):
        """Validate value, max, min."""
        if self.min > new or new > self.max:
            self.value = min(max(new, self.min), self.max)


class IntText(_Int):
    _view_name = Unicode('IntTextView', sync=True)


class BoundedIntText(_BoundedInt):
    _view_name = Unicode('IntTextView', sync=True)


class IntSlider(_BoundedInt):
    _view_name = Unicode('IntSliderView', sync=True)
    orientation = Enum([u'horizontal', u'vertical'], u'horizontal', 
        help="Vertical or horizontal.", sync=True)
    readout = Bool(True, help="Display the current value of the slider next to it.", sync=True)


class IntProgress(_BoundedInt):
    _view_name = Unicode('ProgressView', sync=True)

_IntWidget = DeprecatedClass(_Int, '_IntWidget')
_BoundedIntWidget = DeprecatedClass(_BoundedInt, '_BoundedIntWidget')
IntTextWidget = DeprecatedClass(IntText, 'IntTextWidget')
BoundedIntTextWidget = DeprecatedClass(BoundedIntText, 'BoundedIntTextWidget')
IntSliderWidget = DeprecatedClass(IntSlider, 'IntSliderWidget')
IntProgressWidget = DeprecatedClass(IntProgress, 'IntProgressWidget')
