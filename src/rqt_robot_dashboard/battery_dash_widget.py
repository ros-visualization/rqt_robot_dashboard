# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import os
import rospkg
from python_qt_binding.QtCore import Signal, QSize
from python_qt_binding.QtGui import QIcon, QLabel
from .util import IconHelper

class BatteryDashWidget(QLabel):
    
    state_changed = Signal(int)
    """
    A Widget which displays incremental battery state, including a status tip.
    To use this widget simply call :func:`update_perc` and :func:`update_time` to change the displayed charge percentage and time remaining, respectively.

    :param name: The name of this widget
    :type name: str
    """
    def __init__(self, name='Battery', icons=None, charge_icons=None, icon_paths=None, suppress_overlays=False):
        super(BatteryDashWidget, self).__init__()
        if icons == None:
            icons = []
            charge_icons = []
            for x in range(6):
                icons.append(['ic-battery-%s.svg' % (x * 20)])
                charge_icons.append(['ic-battery-charge-%s.svg' % (x * 20)])
        icon_paths = (icon_paths if icon_paths else []) + [['rqt_robot_dashboard', 'images']]
        paths = []
        for path in icon_paths:
            paths.append(os.path.join(rospkg.RosPack().get_path(path[0]), path[1]))
        self._icon_helper = IconHelper(paths)
        self.set_icon_lists(icons, charge_icons, suppress_overlays)
        self._name = name
        self._charging = False
        self.__state = 0
        self.setMargin(5)
        self.state_changed.connect(self._update_state)
        self.update_perc(0)
        self.update_time(0)

    def _update_state(self, state):
        if self._charging:
            self.setPixmap(self._charge_icons[state].pixmap(QSize(60, 100)))
        else:
            self.setPixmap(self._icons[state].pixmap(QSize(60, 100)))
    
    @property
    def state(self):
        """
        Read-only accessor for the widgets current state.
        """
        return self.__state
        
    def set_icon_lists(self, icons, charge_icons=None, suppress_overlays=False):
        """
        Sets up the icon lists for the button states.
        There must be one index in icons for each state.
        
        :raises IndexError: if ``icons`` is not a list of lists of strings
        
        :param icons: A list of lists of strings to create icons for the states of this button.\
        If only one is supplied then ok, warn, error, stale icons will be created with overlays
        :type icons: list
        :param charge_icons: A list of clicked state icons. len must equal icons
        :type charge_icons: list
        :param suppress_overlays: if false and there is only one icon path supplied
        :type suppress_overlays: bool
        """
        if charge_icons is not None and len(icons) != len(charge_icons):
            rospy.logerr("%s: icons and clicked states are unequal" % self._name)
            icons = charge_icons = ['ic-missing-icon.svg']
        if not (type(icons) is list and type(icons[0]) is list and type(icons[0][0] is str)):
            raise(IndexError("icons must be a list of lists of strings"))
        if len(icons) <= 0:
            rospy.logerr("%s: Icons not supplied" % self._name)
            icons = charge_icons = ['ic-missing-icon.svg']
        if len(icons) == 1 and suppress_overlays == False:
            if icons[0][0][-4].lower() == '.svg':
                icons.append(icons[0] + ['ol-warn-badge.svg'])
                icons.append(icons[0] + ['ol-err-badge.svg'])
                icons.append(icons[0] + ['ol-stale-badge.svg'])
            else:
                icons.append(icons[0] + ['warn-overlay.png'])
                icons.append(icons[0] + ['err-overlay.png'])
                icons.append(icons[0] + ['stale-overlay.png'])
        if charge_icons is None:
            charge_icons = []
            for name in icons:
                charge_icons.append(name + ['ol-click.svg'])
        self._icons = []
        for icon in icons:
            self._icons.append(self._icon_helper.build_icon(icon))
        self._charge_icons = []
        for icon in charge_icons:
            self._charge_icons.append(self._icon_helper.build_icon(icon))

    def set_charging(self, value):
        self._charging = value

    def update_perc(self, val):
        """Update the displayed battery percentage.
        The default implementation of this method displays in 20% increments

        :param val: The new value to be displayed.
        :type val: int
        """
        self.update_state(round(val / 20.0))

    def update_state(self, state):
        """
        Set the state of this button.
        This will also update the icon for the button based on the ``self._icons`` list

        :raises IndexError: If state is not a proper index to ``self._icons``

        :param state: The state to set.
        :type state: int
        """
        if 0 <= state and state < len(self._icons):
            self.__state = state
            self.state_changed.emit(self.__state)
        else:
            raise IndexError("%s update_state received invalid state: %s" % (self._name, state))

    def update_time(self, value):
        try:
            fval = float(value)
            self.setToolTip("%s: %.2f%% remaining" % (self._name, fval))
        except ValueError:
            self.setToolTip("%s: %s%% remaining" % (self._name, value))
