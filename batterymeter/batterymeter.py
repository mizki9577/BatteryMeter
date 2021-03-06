#!/usr/bin/env python3
"""
A battery meter. Works on systray.
"""

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QErrorMessage, QStyle
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QLinearGradient

MENU_EXIT_ITEM_LABEL = 'Exit'
INTERVAL_MS = 1000
CHARGING = 'Charging'
DISCHARGING = 'Discharging'
FULL = 'Full'
UNKNOWN = 'Unknown'


class BatteryMeter(object):

    """
    A Batterry Meter.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Check system tray support
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._errmsg('There is no system tray.', connect=sys.exit)

        # Tray Icon
        self.trayicon = QSystemTrayIcon()
        self.trayicon.show()
        self.trayicon_size = self.trayicon.geometry().width()

        # Context menu
        context_menu = QMenu()
        exit_icon = self.app.style().standardIcon(QStyle.StandardPixmap(QStyle.SP_DockWidgetCloseButton))
        item_exit = context_menu.addAction(exit_icon, MENU_EXIT_ITEM_LABEL)
        item_exit.triggered.connect(self.app.quit)
        self.trayicon.setContextMenu(context_menu)

        # Color
        self.background_color = QColor(0, 0, 0)
        middle_color = QColor(255, 255, 0)
        low_color = QColor(255, 0, 0)
        self.full_color = QColor(0, 255, 0)
        self.charging_color = QColor(0, 0, 255)

        # Gradient Brush
        gradient = QLinearGradient(
            self.trayicon_size / 2,
            0,
            self.trayicon_size / 2,
            self.trayicon_size
        )
        gradient.setColorAt(0, self.full_color)
        gradient.setColorAt(0.75, middle_color)
        gradient.setColorAt(1, low_color)
        self.graph_brush = QBrush(gradient)

        # Pixmap and Painter
        self.graph_pixmap = QPixmap(self.trayicon_size, self.trayicon_size)
        self.graph_pixmap.fill()
        self.graph_painter = QPainter(self.graph_pixmap)
        self.graph_painter.setBackground(QBrush(self.background_color))

        # Timer
        timer = QTimer()
        timer.timeout.connect(self.refresh)
        timer.start(INTERVAL_MS)

        # Start
        sys.exit(self.app.exec())

    def refresh(self):
        """Draw graph, and refresh the tray icon."""
        self.graph_painter.eraseRect(0, 0, self.trayicon_size, self.trayicon_size)
        self.rate = self.battery_energy_rate()

        try:
            battery_status = self.battery_status()
        except BatteryStatusError as e:
            self.trayicon.showMessage('battery-meter', str(e))
            battery_status = UNKNOWN

        if battery_status is CHARGING:
            graph_color = self.charging_color
        elif battery_status is DISCHARGING:
            graph_color = self.graph_brush
        elif battery_status is FULL:
            graph_color = self.full_color
        elif battery_status is UNKNOWN:
            graph_color = self.graph_brush

        self.graph_painter.fillRect(
            0,
            self.trayicon_size,
            self.trayicon_size,
            - self.rate * self.trayicon_size,
            graph_color
        )

        self.trayicon.setIcon(QIcon(self.graph_pixmap))
        self.trayicon.setToolTip('{} {:6.2f} %'.format(battery_status, self.rate * 100))
        return

    def battery_energy_rate(self):
        """Return battery energy rate."""
        try:
            return self.battery_energy_now() / self.battery_energy_full()
        except FileNotFoundError as e:
            self._errmsg(str(e))

    def battery_energy_full(self):
        """Return battery enagy in full."""
        return int(open('/sys/class/power_supply/BAT0/energy_full').read())

    def battery_energy_now(self):
        """Return current battery energy."""
        return int(open('/sys/class/power_supply/BAT0/energy_now').read())

    def battery_status(self):
        """Return True if battery is charging."""
        status = open('/sys/class/power_supply/BAT0/status').read()
        if status == 'Charging\n':
            return CHARGING
        elif status == 'Discharging\n':
            return DISCHARGING
        elif status == 'Full\n':
            return FULL
        elif status == 'Unknown\n':
            return UNKNOWN
        else:
            raise BatteryStatusError(status)

    def _errmsg(self, msg, connect=None):
        """
        Display error dialog window.
        In default, the application will shut down when the dialog window will be closed.
        """
        #ひどい英語だ
        errmsg = QErrorMessage()
        if connect is None:
            connect = self.app.quit
        errmsg.finished.connect(connect)
        errmsg.showMessage(msg)
        errmsg.exec()


class BatteryStatusError(ValueError):

    """Error when BatteryMeter gots unknown battery status."""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return 'Unknown battery status ({}) has returned.'.format(self.status)
