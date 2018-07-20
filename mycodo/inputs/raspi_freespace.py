# coding=utf-8
import logging

import os

from .base_input import AbstractInput
from .sensorutils import convert_units


class RaspberryPiFreeSpace(AbstractInput):
    """ A sensor support class that monitors the free space of a path """

    def __init__(self, input_dev, testing=False):
        super(RaspberryPiFreeSpace, self).__init__()
        self.logger = logging.getLogger("mycodo.inputs.raspi_freespace")
        self._disk_space = None

        if not testing:
            self.logger = logging.getLogger(
                "mycodo.inputs.raspi_freespace_{id}".format(id=input_dev.id))
            self.path = input_dev.location
            self.convert_to_unit = input_dev.convert_to_unit

    def __repr__(self):
        """  Representation of object """
        return "<{cls}(disk_space={disk_space})>".format(
            cls=type(self).__name__,
            disk_space="{0:.2f}".format(self._disk_space))

    def __str__(self):
        """ Return CPU load information """
        return "Free Space: {disk_space}".format(
            disk_space="{:.2f}".format(self._disk_space))

    def __iter__(self):  # must return an iterator
        """ RaspberryPiFreeSpace iterates through free space readings """
        return self

    def next(self):
        """ Get next free space reading """
        if self.read():  # raised an error
            raise StopIteration  # required
        return dict(disk_space=float('{0:.2f}'.format(self._disk_space)))

    @property
    def disk_space(self):
        """ Free space of self.path """
        if self._disk_space is None:  # update if needed
            self.read()
        return self._disk_space

    def get_measurement(self):
        """ Gets the free space """
        f = os.statvfs(self.path)
        space_mb = (f.f_bsize * f.f_bavail) / 1000000.0
        space = convert_units(
            'disk_space', 'MB', self.convert_to_unit,
            space_mb)
        return space

    def read(self):
        """
        Takes a reading and updates the self._disk_space value

        :returns: None on success or 1 on error
        """
        try:
            self._disk_space = self.get_measurement()
            if self._disk_space is not None:
                return  # success - no errors
        except Exception as e:
            self.logger.exception(
                "{cls} raised an exception when taking a reading: "
                "{err}".format(cls=type(self).__name__, err=e))
        return 1
