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

from python_qt_binding.QtGui import QIcon, QImage, QPainter, QPixmap
from python_qt_binding.QtWidgets import QMessageBox
from python_qt_binding.QtSvg import QSvgRenderer


def dashinfo(logger, msg, obj, title='Info'):
    """
    Logs a message with ``logger.info`` and displays a ``QMessageBox`` to the user

    :param msg: Message to display.
    :type msg: str
    :param obj: Parent object for the ``QMessageBox``
    :type obj: QObject
    :param title: An optional title for the `QMessageBox``
    :type title: str
    """
    logger.info(msg)

    box = QMessageBox()
    box.setText(msg)
    box.setWindowTitle(title)
    box.show()

    obj._message_box = box


def dashwarn(logger, msg, obj, title='Warning'):
    """
    Logs a message with ``logger.warning`` and displays a ``QMessageBox`` to the user

    :param msg: Message to display.
    :type msg: str
    :param obj: Parent object for the ``QMessageBox``
    :type obj: QObject
    :param title: An optional title for the `QMessageBox``
    :type title: str
    """
    logger.warning(msg)

    box = QMessageBox()
    box.setText(msg)
    box.setWindowTitle(title)
    box.show()

    obj._message_box = box


def dasherr(logger, msg, obj, title='Error'):
    """
    Logs a message with ``logger.error`` and displays a ``QMessageBox`` to the user

    :param msg: Message to display.
    :type msg: str
    :param obj: Parent object for the ``QMessageBox``
    :type obj: QObject
    :param title: An optional title for the `QMessageBox``
    :type title: str
    """
    logger.error(msg)

    box = QMessageBox()
    box.setText(msg)
    box.setWindowTitle(title)
    box.show()

    obj._message_box = box


class IconHelper(object):
    """
    Helper class to easily access images and build QIcons out of lists of file names
    """
    def __init__(self, context, paths=None, name="IconHelper"):
        self.logger = context.node.get_logger()
        self._image_paths = paths if paths else []
        self._name = name

    def add_image_path(self, path):
        """
        Paths added will be searched for images by the _find_image function
        Paths will be searched in revearse order by add time
        The last path to be searched is always rqt_robot_dashboard/images
        Subdirectories are not recursively searched

        :param path: The path to add to the image paths list
        :type path: str
        """
        self._image_paths = [path] + self._image_paths

    def make_icon(self, image_list, mode=QIcon.Normal, state=QIcon.On):
        """
        Helper function to create QIcons from lists of image files
        Warning: svg files interleaved with other files will not render correctly

        :param image_list: list of image paths to layer into an icon.
        :type image: list of str
        :param mode: The mode of the QIcon to be created.
        :type mode: int
        :param state: the state of the QIcon to be created.
        :type state: int
        """
        if type(image_list) is not list:
            image_list = [image_list]
        if len(image_list) <= 0:
            raise TypeError('The list of images is empty.')

        num_svg = 0
        for item in image_list:
            if item[-4:].lower() == '.svg':
                num_svg = num_svg + 1

        if num_svg != len(image_list):
            # Legacy support for non-svg images
            icon_pixmap = QPixmap()
            icon_pixmap.load(image_list[0])
            painter = QPainter(icon_pixmap)
            for item in image_list[1:]:
                painter.drawPixmap(0, 0, QPixmap(item))
            icon = QIcon()
            icon.addPixmap(icon_pixmap, mode, state)
            painter.end()
            return icon
        else:
            #  rendering SVG files into a QImage
            renderer = QSvgRenderer(image_list[0])
            icon_image = QImage(renderer.defaultSize(), QImage.Format_ARGB32)
            icon_image.fill(0)
            painter = QPainter(icon_image)
            renderer.render(painter)
            if len(image_list) > 1:
                for item in image_list[1:]:
                    renderer.load(item)
                    renderer.render(painter)
            painter.end()
            #  Convert QImage into a pixmap to create the icon
            icon_pixmap = QPixmap()
            icon_pixmap.convertFromImage(icon_image)
            icon = QIcon(icon_pixmap)
            return icon

    def find_image(self, path):
        """
        Convenience function to help with finding images.
        Path can either be specified as absolute paths or relative to any path in ``_image_paths``

        :param path: The path or name of the image.
        :type path: str
        """
        if os.path.exists(path):
            return path
        for image_path in self._image_paths:
            if os.path.exists(os.path.join(image_path, path)):
                return os.path.join(image_path, path)
            elif '.' in path and os.path.exists(os.path.join(image_path, 'nonsvg', path)):
                return os.path.join(image_path, 'nonsvg', path)
        return os.path.join(self._image_paths[-1], 'ic-missing-icon.svg')

    def build_icon(self, image_name_list, mode=QIcon.Normal, state=QIcon.On):
        """
        Convenience function to create an icon from a list of file names

        :param image_name_list: List of file image names to make into an icon
        :type image_name_list: list of str
        :param mode: The mode of the QIcon to be created.
        :type mode: int
        :param state: the state of the QIcon to be created.
        :type state: int
        """
        found_list = []
        for name in image_name_list:
            found_list.append(self.find_image(name))
        return self.make_icon(found_list, mode, state)

    def set_icon_lists(self, icons, clicked_icons=None, suppress_overlays=False):
        """
        Sets up the icon lists for the button states.
        There must be one index in icons for each state.

        :raises IndexError: if ``icons`` is not a list of lists of strings

        :param icons: A list of lists of strings to create icons for the states of this button.\
        If only one is supplied then ok, warn, error, stale icons will be created with overlays
        :type icons: list
        :param clicked_icons: A list of clicked state icons. len must equal icons
        :type clicked_icons: list
        :param suppress_overlays: if false and there is only one icon path supplied
        :type suppress_overlays: bool
        """
        if clicked_icons is not None and len(icons) != len(clicked_icons):
            self.logger.error("%s: icons and clicked states are unequal" % self._name)
            icons = clicked_icons = [['ic-missing-icon.svg']]
        if not (type(icons) is list and type(icons[0]) is list and type(icons[0][0] is str)):
            raise(IndexError("icons must be a list of lists of strings"))
        if len(icons) <= 0:
            self.logger.error("%s: Icons not supplied" % self._name)
            icons = clicked_icons = ['ic-missing-icon.svg']
        if len(icons) == 1 and suppress_overlays == False:
            if icons[0][0][-4].lower() == '.svg':
                icons.append(icons[0] + ['ol-warn-badge.svg'])
                icons.append(icons[0] + ['ol-err-badge.svg'])
                icons.append(icons[0] + ['ol-stale-badge.svg'])
            else:
                icons.append(icons[0] + ['warn-overlay.png'])
                icons.append(icons[0] + ['err-overlay.png'])
                icons.append(icons[0] + ['stale-overlay.png'])
        if clicked_icons is None:
            clicked_icons = []
            for name in icons:
                clicked_icons.append(name + ['ol-click.svg'])
        icons_conv = []
        for icon in icons:
            icons_conv.append(self.build_icon(icon))
        clicked_icons_conv = []
        for icon in clicked_icons:
            clicked_icons_conv.append(self.build_icon(icon))
        return (icons_conv, clicked_icons_conv)
