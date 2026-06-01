"""ResultsFile: read a results .h5 written by the exporter.

Gives easy access to each stored result and to its parameters and provenance,
so a saved analysis can be inspected and reproduced.
"""


class ResultsFile:
    """Reader for a results .h5 file.

    Parameters
    ----------
    path : str
        Path to a results file written by ``io.exporter``.

    Attributes
    ----------
    provenance : dict
        The Provenance block (input files, pipeline, params, config, ...).
    devices : list of str
        Devices present in the file.
    """

    def __init__(self, path):
        self.path = path
        self.provenance = None
        self.devices = []
        raise NotImplementedError

    def analyses(self, device):
        """List the analyses stored for a device."""
        raise NotImplementedError

    def get(self, device, analysis):
        """Return ``(data, params)`` for one stored result."""
        raise NotImplementedError
