#!/usr/bin/env python3
# coding: utf-8
"""
Created on Wed May 27 19:00:12 2020
Description: Script to convert NetCDF4 to COG GeoTiff
Use: 
    python nc2cog.py [nc input file]
@author: javier.concha, Javier.Concha@artov.ismar.cnr.it
"""
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


'''
example nc file:
netcdf nas-chl-anomaly_w_08-28Mar-03Apr {
dimensions:
    lat = 480 ;
    lon = 474 ;
variables:
    float lat(lat) ;
    float lon(lon) ;
    float anomaly(lat, lon) ;
        anomaly:_FillValue = -999.f ;

// global attributes:
        :history = "Sat May 23 21:15:29 2020: ncatted -O -a _FillValue,anomaly,o,f,-999 /Users/scolella/Work/data/snapshot/prod/nas-chl-anomaly_w_08-28Mar-03Apr.nc" ;
}'''
    
import sys    
import os
    
#Import gdal
from osgeo import gdal
from osgeo import osr

def export_geotiff(netcdf_file):
    geotiff_file = netcdf_file.split('.')[0]+'_cog.tif'
    
    #Open existing dataset
    src_ds = gdal.Open(netcdf_file)
    
    #Open output format driver, see gdal_translate --formats for list
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    
    #Output to new format
    dst_ds = driver.CreateCopy('intermediate.tif', src_ds, 1 )
    srs = osr.SpatialReference()            # establish encoding
    srs.ImportFromEPSG(4326)                # WGS84 lat/lon
    dst_ds.SetProjection(srs.ExportToWkt()) # export coords to file

    dst_ds = None
    src_ds = None
    
    # - Resize the pixel resolution yRes=xRes
    # gdal_translate -tr x y inputfile outputfile
    # - Adding no data value needed for COG
    # gdal_translate -of GTIFF inputfile.tif intermediate.tif -a_nodata -999
    ds = gdal.Open('intermediate.tif')
    gt = ds.GetGeoTransform()
    pixelSizeX = gt[1]
    pixelSizeY =-gt[5]
    print(f'original: xRes:{pixelSizeX},yRes:{pixelSizeY}')
    pixelSize = 0.003848075866699
    ds = gdal.Translate('intermediate2.tif',ds,xRes=pixelSize,yRes=pixelSize,noData=-999)
    gt = ds.GetGeoTransform()
    pixelSizeX = gt[1]
    pixelSizeY =-gt[5]
    print(f'new: xRes:{pixelSizeX},yRes:{pixelSizeY}')
    # # dst_ds.GetRasterBand(1).SetDescription('anomaly') 
    ds.SetMetadataItem('AREA_OR_POINT','Area','')
    ds.SetMetadataItem('TIFFTAG_RESOLUTIONUNIT', '1 (unitless)','')
    ds.SetMetadataItem('TIFFTAG_XRESOLUTION', '1','')
    ds.SetMetadataItem('TIFFTAG_YRESOLUTION', '1','')
    
    # - Add the overviews zoom levels 
    # (gdaladdo -r average --config GDAL_TIFF_OVR_BLOCKSIZE 1024 intermediate.tiff 2 4 8 16 32)
    gdal.SetConfigOption('GDAL_TIFF_OVR_BLOCKSIZE', '1024')
    ds.BuildOverviews("AVERAGE", [2,4,8,16,32])

    ds = None
    # - Compression of tif 
    # (gdal_translate -co TILED=YES -co COPY_SRC_OVERVIEWS=YES --config GDAL_TIFF_OVR_BLOCKSIZE 1024 -co BLOCKXSIZE=1024 -co BLOCKYSIZE=1024 -co COMPRESS=DEFLATE intermediate.tiff outputfile.tiff)
  
    ds2 = gdal.Open('intermediate2.tif')
    gdal.SetConfigOption('GDAL_TIFF_OVR_BLOCKSIZE', '1024')
    creation_options = ['TILED=YES','COPY_SRC_OVERVIEWS=YES', 'BLOCKXSIZE=1024', 'BLOCKYSIZE=1024','COMPRESS=DEFLATE']
    ds2 = gdal.Translate(geotiff_file,ds2,creationOptions= creation_options)

    ds2 =None
    os.remove("intermediate.tif")
    os.remove("intermediate2.tif")
    
#%%
if __name__ == "__main__":
    # Example:
    # netcdf_file = 'nas-chl-anomaly_w_08-28Mar-03Apr.nc'
    
    
    if len(sys.argv) != 2:
        print('Use: python nc2cog.py [nc input file]')
        exit()
        
    netcdf_file = sys.argv[1]
    export_geotiff(netcdf_file)
