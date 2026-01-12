from . import _de265  # type: ignore
from ._de265 import (  # type: ignore
    get_version, 
    get_error_text, 
    isOk, 
    set_verbosity,
    de265_error as Error,
    de265_chroma as ChromaFormat,
    de265_param as Parameter
)

class Image:
    """
    A wrapper around de265_image.
    """
    def __init__(self, internal_image):
        self._img = internal_image

    @property
    def pts(self):
        return self._img.pts

    @property
    def chroma_format(self):
        return self._img.chroma_format

    def width(self, channel=0):
        return self._img.get_width(channel)

    def height(self, channel=0):
        return self._img.get_height(channel)

    def get_bits_per_pixel(self, channel=0):
        return self._img.get_bits_per_pixel(channel)

    def plane(self, channel):
        """
        Returns a numpy array (memory view) for the specified channel.
        channel 0: Y, 1: Cb, 2: Cr.
        """
        return self._img.get_plane(channel)

    def yuv(self):
        """
        Returns a tuple of (Y, Cb, Cr) planes as numpy arrays.
        """
        # CHROMA_MONO only has one plane
        if self.chroma_format == ChromaFormat.CHROMA_MONO:
            return (self.plane(0), None, None)
        return (self.plane(0), self.plane(1), self.plane(2))

    def nal_header(self):
        return self._img.get_nal_header()

    @property
    def full_range(self): return self._img.full_range
    
    @property
    def colour_primaries(self): return self._img.colour_primaries
    
    @property
    def transfer_characteristics(self): return self._img.transfer_characteristics
    
    @property
    def matrix_coefficients(self): return self._img.matrix_coefficients

    def to_rgb(self):
        """
        Returns an RGB image as a numpy array.
        Conversion is performed in C++ for performance.
        """
        return self._img.to_rgb()

    def get_image_ptr(self):
        return self._img.get_image_ptr()

class decoder:
    """
    The main decoder class.
    """
    def __init__(self, threads=0):
        self._decoder = _de265.decoder()
        if threads > 0:
            self._decoder.start_worker_threads(threads)

    def push_data(self, data, pts=0):
        """
        Push raw HEVC bitstream data into the decoder.
        """
        err = self._decoder.push_data(data, pts)
        if not isOk(err):
            raise RuntimeError(f"libde265 error: {get_error_text(err)}")

    def push_end_of_NAL(self):
        self._decoder.push_end_of_NAL()

    def push_end_of_frame(self):
        self._decoder.push_end_of_frame()

    def flush(self):
        """
        Flush remaining data and finish decoding.
        """
        err = self._decoder.flush_data()
        if not isOk(err):
            raise RuntimeError(f"libde265 error: {get_error_text(err)}")

    def decode(self):
        """
        Yields decoded images from currently buffered data.
        """
        while True:
            err, more = self._decoder.decode()
            
            # Pull all available pictures
            while True:
                img = self._decoder.get_next_picture()
                if img is None:
                    break
                yield Image(img)

            if not more:
                break
            
            if err == Error.ERROR_WAITING_FOR_INPUT_DATA:
                break
            elif not isOk(err):
                # We could raise or log warning
                break

    def load_file(self, path, buffer_size=1024*1024):
        """
        Convenience method to decode a whole file.
        """
        with open(path, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                self.push_data(data)
                yield from self.decode()
        
        self.flush()
        yield from self.decode()

    def reset(self):
        self._decoder.reset()

    def get_number_of_input_bytes_pending(self):
        return self._decoder.get_number_of_input_bytes_pending()

    @property
    def highest_tid(self): return self._decoder.get_highest_TID()
    
    @property
    def current_tid(self): return self._decoder.get_current_TID()

    def set_limit_tid(self, tid):
        self._decoder.set_limit_TID(tid)

    def set_parameter(self, param, value):
        if isinstance(value, bool):
            self._decoder.set_parameter_bool(param, value)
        else:
            self._decoder.set_parameter_int(param, int(value))

    def get_parameter(self, param):
        # Only bool param getter exposed in C++ currently, let's keep it simple
        return self._decoder.get_parameter_bool(param)
