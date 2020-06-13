import zlib
from django.core.cache import cache


class Zip(object):

    level = 9
    # For Zlib we use negative value for window bits. This gets rid of the
    # checksum at the end, which allows us to swap blocks around at will.
    wbits = -15
    
    @staticmethod
    def store(compressor,key,data,time=None):
        zData = compressor.compress(data)
        zData += compressor.flush(zlib.Z_FULL_FLUSH)
        cache.set(key, zData, time)
        return zData
    
    def inflate(self,decompressor,data):
        return self.decompressor.decompress(data)


    def get_decompressor(self,request):
        try:
            self.encoding = request.META['HTTP_ACCEPT_ENCODING']
        except:
            self.encoding = ''
        self.decompressor = zlib.decompressobj(wbits=self.wbits)
        if 'deflate' in self.encoding:
            self.decompressor = None
        else:
            self.decompressor = zlib.decompressobj(wbits=self.wbits)
