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

from diagnostic_msgs.msg import DiagnosticStatus
from python_qt_binding.QtCore import QMutex, QMutexLocker, QSize, QTimer, Signal
from rqt_robot_monitor.robot_monitor import RobotMonitorWidget
from .icon_tool_button import IconToolButton


class MonitorDashWidget(IconToolButton):
    """
    A widget which brings up the rqt_robot_monitor.

    Times out after certain period of time (set as 5 sec as of Apr 2013)
    without receiving diagnostics msg ('/diagnostics_toplevel_state' of
    DiagnosticStatus type), status becomes as 'stale'.

    :param context: The plugin context to create the monitor in.
    :type context: qt_gui.plugin_context.PluginContext
    """
    _msg_trigger = Signal()

    def __init__(self, context, icon_paths=[]):
        self._graveyard = []
        ok_icon = ['bg-green.svg', 'ic-diagnostics.svg']
        warn_icon = ['bg-yellow.svg', 'ic-diagnostics.svg',
                     'ol-warn-badge.svg']
        err_icon = ['bg-red.svg', 'ic-diagnostics.svg', 'ol-err-badge.svg']
        stale_icon = ['bg-grey.svg', 'ic-diagnostics.svg',
                      'ol-stale-badge.svg']

        icons = [ok_icon, warn_icon, err_icon, stale_icon]

        super(MonitorDashWidget, self).__init__(context, 'MonitorWidget', icons,
                                                icon_paths=icon_paths)

        self.setFixedSize(self._icons[0].actualSize(QSize(50, 30)))

        self._monitor = None
        self._close_mutex = QMutex()
        self._show_mutex = QMutex()

        self._last_update = context.node.get_clock().now()

        self.context = context
        self.clicked.connect(self._show_monitor)

        self._monitor_shown = False
        self.setToolTip('Diagnostics')

        self._diagnostics_toplevel_state_sub = context.node.create_subscription(DiagnosticStatus,
                                                                                'diagnostics_toplevel_state',
                                                                                self.toplevel_state_callback, 10)

        self._top_level_state = -1
        self._stall_timer = QTimer()
        self._stall_timer.timeout.connect(self._stalled)
        self._stalled()
        self._plugin_settings = None
        self._instance_settings = None
        self._msg_trigger.connect(self._handle_msg_trigger)

    def toplevel_state_callback(self, msg):
        self._is_stale = False
        self._msg_trigger.emit()

        level = int.from_bytes(msg.level, byteorder='big')

        if self._top_level_state != level:
            if (level >= 2):
                self.update_state(2)
                self.setToolTip("Diagnostics: Error")
            elif (level == 1):
                self.update_state(1)
                self.setToolTip("Diagnostics: Warning")
            else:
                self.update_state(0)
                self.setToolTip("Diagnostics: OK")
            self._top_level_state = level

    def _handle_msg_trigger(self):
        self._stall_timer.start(5000)

    def _stalled(self):
        self._stall_timer.stop()
        self._is_stale = True
        self.update_state(3)
        self._top_level_state = 3
        self.setToolTip("Diagnostics: Stale\nNo message received on "
                        "/diagnostics_agg in the last 5 seconds")

    def _show_monitor(self):
        with QMutexLocker(self._show_mutex):
            try:
                if self._monitor_shown:
                    self.context.remove_widget(self._monitor)
                    self._monitor_close()
                    self._monitor_shown = False
                else:
                    self._monitor = RobotMonitorWidget(self.context,
                                                       '/diagnostics_agg')
                    if self._plugin_settings:
                        self._monitor.restore_settings(self._plugin_settings,
                                                       self._instance_settings)
                    self.context.add_widget(self._monitor)
                    self._monitor_shown = True
            except Exception:
                if self._monitor_shown == False:
                    raise
                #TODO: when closeEvents is available fix this hack
                # (It ensures the button will toggle correctly)
                self._monitor_shown = False
                self._show_monitor()

    def _monitor_close(self):
        if self._monitor_shown:
            with QMutexLocker(self._close_mutex):
                if self._plugin_settings:
                    self._monitor.save_settings(self._plugin_settings,
                                                self._instance_settings)
                self._monitor.shutdown()
                self._monitor.close()
                self._graveyard.append(self._monitor)
                self._monitor = None

    def shutdown_widget(self):
        self._stall_timer.stop()
        if self._monitor:
            self._monitor.shutdown()

    def save_settings(self, plugin_settings, instance_settings):
        if self._monitor_shown:
            self._monitor.save_settings(self._plugin_settings,
                                        self._instance_settings)

    def restore_settings(self, plugin_settings, instance_settings):
        self._plugin_settings = plugin_settings
        self._instance_settings = instance_settings
