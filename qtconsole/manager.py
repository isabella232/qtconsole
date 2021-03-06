""" Defines a KernelClient that provides signals and slots.
"""

from qtpy import QtCore

# Local imports
from traitlets import Bool, DottedObjectName

from jupyter_client import KernelManager
from jupyter_client.restarter import KernelRestarter

from .kernel_mixins import QtKernelManagerMixin, QtKernelRestarterMixin


class QtKernelRestarter(KernelRestarter, QtKernelRestarterMixin):

    def start(self):
        if self._timer is None:
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(self.poll)
        self._timer.start(round(self.time_to_dead * 1000))

    def stop(self):
        self._timer.stop()

    def poll(self):
        super().poll()


class QtKernelManager(KernelManager, QtKernelManagerMixin):
    """A KernelManager with Qt signals for restart"""

    client_class = DottedObjectName('qtconsole.client.QtKernelClient')
    autorestart = Bool(True, config=True)

    def start_restarter(self):
        if self.autorestart and self.has_kernel:
            if self._restarter is None:
                self._restarter = QtKernelRestarter(
                    kernel_manager=self,
                    parent=self,
                    log=self.log,
                )
                self._restarter.add_callback(self._handle_kernel_restarted)
            self._restarter.start()

    def stop_restarter(self):
        if self.autorestart:
            if self._restarter is not None:
                self._restarter.stop()

    def _handle_kernel_restarted(self):
        self.kernel_restarted.emit()
