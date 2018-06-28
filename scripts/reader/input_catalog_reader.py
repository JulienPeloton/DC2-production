"""
input_catalog_reader
"""
import os
import numpy as np
from GCR import BaseGenericCatalog

__all__ = ['InputCatalogReader']

class InputCatalogReader(BaseGenericCatalog):
    """Input catalog reader.
    Optinal options:
       filename -- which file to use
       nlines -- how many lines to read at once
       only_first_chuck -- If the reader should only read the first chunk. 
                           Set to `True` if you don't need the entire file!
   """

    def _subclass_init(self, **kwargs):
        self._filename = kwargs.get(
            'filename',
            '/global/projecta/projectdirs/lsst/groups/SSim/DC2/reference_catalogs/dc2_reference_catalog_dc2v3_fov4.txt'
        )
        
        if not os.path.isfile(self._filename):
            raise ValueError('File {} not found'.format(self._filename))

        self._nlines = int(kwargs.get('nlines', 10000))
        self._only_first_chuck = bool(kwargs.get('only_first_chuck', False))

        self._quantity_modifiers = {
            'ra' : 'raJ2000',
            'dec' : 'decJ2000',
            'sigma_ra' : 'sigma_raJ2000',
            'sigma_dec' : 'sigma_decJ2000',
            'ra_smeared' : 'raJ2000_smeared',
            'dec_smeared' : 'decJ2000_smeared',
        }

        self._header_line_number = 0
        self._data_dtype = None


    def _iter_native_dataset(self, native_filters=None):
        if native_filters is not None:
            raise ValueError('`native_filter` not supported!')

        with open(self._filename, 'rb') as f:
            for i in range(self._header_line_number):
                next(f)
                
            while True:
                data = np.genfromtxt(f, self._data_dtype, delimiter=',', max_rows=self._nlines)
                if len(data) == 0:
                    break
                yield data.__getitem__
                if self._only_first_chuck:
                    break
                

    def _generate_native_quantity_list(self, native_filters = None):
        with open(self._filename, 'r') as f:
            for i, line in enumerate(f):
                if len(line) > 2 and line[0] == '#'  and line[1] not in (' ', '\n'):
                    self._header_line_number = i + 1
                    break #found the header line!

        fields = [field.strip() for field in line[1:].split(',')]
        self._data_dtype = np.dtype([(field, np.int if field.startswith('is') or field.endswith('Id') else np.float) for field in fields])
        return fields
