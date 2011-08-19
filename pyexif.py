import pyexiv2
#We then load an image file and read its metadata:

metadata = pyexiv2.ImageMetadata('test.jpg')
metadata.read()
#Reading and writing EXIF tags
#Let’s retrieve a list of all the available EXIF tags available in the image:


print 
""
#['Exif.Image.ImageDescription',
# 'Exif.Image.XResolution',
# 'Exif.Image.YResolution',
# 'Exif.Image.ResolutionUnit',
# 'Exif.Image.Software',
# 'Exif.Image.DateTime',
# 'Exif.Image.Artist',
# 'Exif.Image.Copyright',
# 'Exif.Image.ExifTag',
# 'Exif.Photo.Flash',
# 'Exif.Photo.PixelXDimension',
# 'Exif.Photo.PixelYDimension']
#Each of those tags can be accessed with the [] operator on the metadata, much like a python dictionary:

#for v in metadata.exif_keys:
#    print v, " = ", metadata[v].value, " (",metadata[v].raw_value, ")"

if 'Exif.Image.DateTime' in metadata.exif_keys:
    tag = metadata['Exif.Image.DateTime']
#The value of an ExifTag object can be accessed in two different ways: with the #raw_value and with the value attributes:

print tag.raw_value
#'2004-07-13T21:23:44Z'

print tag.value
#datetime.datetime(2004, 7, 13, 21, 23, 44)

