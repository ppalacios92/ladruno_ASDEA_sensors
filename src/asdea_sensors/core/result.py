"""BroadcastResult: a ``{device: result}`` dict that remembers its dataset.

Returned by the broadcast analyses (``ds.fourier()``, ``ds.ambient()``, ...).
It behaves exactly like a dict, so ``amb["MOF00135"]``, iteration and
comprehensions all work; it just also carries a ``.dataset`` back-reference so
the ``*_all`` plots can read the device order, colors and titles without the
caller passing the dataset again.
"""


class BroadcastResult(dict):
    """A result dict keyed by device that knows the dataset it came from."""

    def __init__(self, mapping=(), dataset=None):
        super().__init__(mapping)
        self.dataset = dataset
