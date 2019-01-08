#!/usr/bin/env python3
from pathlib import Path

import cups

from exceptions import (JobCompletedError, JobDocumentNotAvailableError,
                        JobNotFoundError, PrinterNotFoundError)

class BaseCUPS:
    """A basic cups class."""
    def __init__(self):
        self.conn = cups.Connection()


class CUPS(BaseCUPS):
    """A class for a CUPS instance."""

    def get_default(self):
        """Retrieve CUPS' default printer."""
        default_printer = self.conn.getDefault()
        if default_printer:
            return Printer(default_printer)
        return None

    def get_devices(self):
        """Return a list of devices as (deviceclass, deviceinfo, devicemakeandmodel, deviceuri) tuples."""
        # TODO: fix output of this method
        return self.conn.getDevices()

    def get_printers(self):
        """Return the list of print queues names."""
        return [Printer(printer) for printer in self.conn.getPrinters()]

    def get_job_attributes(self):
        """Retrieve a print job's attributes."""
        try:
            jobid = int(jobid)
        except ValueError:
            raise ValueError('Job id should be interger, str is given.')
        return self.conn.getJobAttributes(jobid)

    def get_ppd(self, printer_name):
        """ Retrieve the PPD for the a particular queue name."""
        # TODO : check printer name exist in list of printer
        return self.conn.getPPD(printer_name)

    def get_ppds(self):
        """Return a list of PPDs as (ppdnaturallangugae, ppdmake, ppdmakeandmodel, ppdname) tuples."""
        # TODO: return the output as doc-string
        return self.conn.getPPDs()


class Job(BaseCUPS):
    """A class for managing a CUPS' job."""
    def __init__(self, job_id):
        super().__init__()
        self.job_id = job_id
        # TODO: set job_id property

    def __repr__(self):
        return "Job: <{}>".format(self.job_id)

    def __str__(self):
        return "{}".format(self.job_id)

    @property
    def status(self):
        """Return status of job_id."""
        job_states = {
            3: 'Pending',
            4: 'Pending-held',
            5: 'Processing',
            6: 'Processing-stopped',
            7: 'Canceled',
            8: 'Aborted',
            9: 'Completed',
        }
        try:
            self.attributes = self.conn.getJobAttributes(self.job_id)
        except cups.IPPError:
            raise JobNotFoundError('Job {} does not exist.'.format(self.job_id)) from None
        state = self.attributes['job-state']
        reasons = self.attributes['job-state-reasons']
        try:
            job_state = job_states.get(state) 
            output = job_state if reasons == ['none'] else job_state + " - {}".format(reasons)
        except KeyError:
            output =  'Not detected.'
        return output

    def cancel(self):
        """Cancel a job."""
        try:
            self.conn.cancelJob(self.job_id)
        except cups.IPPError as e:
            raise JobCompletedError('Job {} has been completed.'.format(self.job_id)) from None

    def restart(self):
        """Restart a job."""
        try:
            self.conn.restartJob(self.job_id)
        except cups.IPPError as e:
            raise JobDocumentNotAvailableError("Job's {} document does not exist.".format(self.job_id)) from None

    @staticmethod
    def list():
        """Return a list of CUPS' jobs."""
        def job_number(filename):
            for index, char in enumerate(filename):
                if char not in ('c', '0'):
                    return int(filename[index:])
            return None
        spooldir = Path('/var/spool/cups')
        return [Job(job_number(controlfile.name)) for controlfile in spooldir.glob('c*')]


class Printer(BaseCUPS):
    """A class for managing and handling a CUPS' printer."""
    def __init__(self, name):
        super().__init__()
        self.job_id = None
        self.attributes = None
        self.device_uri = None
        self.location = None
        self.default_message = 'Unable to locate the printer.'
        self.name = name

    def __repr__(self):
        return "Printer: <{}>".format(self.name)

    def __str__(self):
        return "{}".format(self.name)

    def __iter__(self):
        yield from (self.name, self.device_uri, self.location)

    @property
    def valid(self):
        """A printer is valid when it exists in CUPS' Printers."""
        if self.name in self.conn.getPrinters():
            return True
        return False

    @valid.setter
    def valid(self, value):
        """Prevent valid from being setted"""
        raise AttributeError('Valid is not a writable attribute.')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        if self.valid:
            self.attributes = self.conn.getPrinterAttributes(self.name)
            self.device_uri = self.attributes['device-uri']
            self.location = self.attributes['printer-location']

    @property
    def status(self):
        """Return status of the printer."""
        printer_states = {
            3: 'Idle',
            4: 'Processing',
            5: 'Stopped',
        }
        output = self.default_message
        if self.valid:
            state =  self.conn.getPrinterAttributes(self.name)['printer-state']
            reasons = self.conn.getPrinterAttributes(self.name)['printer-state-reasons']
            try:
                printer_state = printer_states.get(state) 
                output = printer_state if reasons == ['none'] else printer_state + " - {}".format(reasons)
            except KeyError:
                output = 'Not detected.'
        return output

    def validate(self):
        """Check if printer is not valid, raise and exception."""
        if not self.valid:
            raise NotImplementedError(self.default_message)

    def delete(self):
        """Delete the printer/queue."""
        self.validate()
        self.conn.deletePrinter(self.name)

    def disable(self):
        """Disable the printer/queue."""
        self.validate()
        self.conn.disablePrinter(self.name)

    def enable(self):
        """Enable the printer/queue."""
        self.validate()
        self.conn.enablePrinter(self.name)

    def add(self):
        """
        Add or adjust a print queue. Several parameters can select which
        PPD to use (filename, ppdname, and ppd, description, location) but only one may be given.
        """
        # TODO: (filename, ppdname, and ppd, description, location)
        self.validate()

    def print(self, filename, title, options):
        """Print a file."""
        self.validate()
        self.job_id = self.conn.printFile(
            self.name,
            filename,
            title,
            options
        )
        return self.job_id

    def export_ppd(self):
        """Export configuration file."""
        self.validate()
