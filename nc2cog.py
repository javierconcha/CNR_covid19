#!/usr/bin/env python3
# coding: utf-8
"""
Created on Wed May 27 19:00:12 2020
Description: Script to convert NetCDF4 to GeoTiff
Use: 
    python nc2tiff.py [nc input file]
@author: javier.concha
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
    
#Import gdal
from osgeo import gdal
from osgeo import osr

def export_geotiff(netcdf_file):
    geotiff_file = netcdf_file.split('.')[0]+'.tif'
    
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
    
    
    ds = gdal.Open('intermediate.tif')
    ds = gdal.Translate(geotiff_file,ds,xRes=0.002712249755859,yRes=0.002712249755859,noData=-999)
    # # dst_ds.GetRasterBand(1).SetDescription('anomaly') 
    # dst_ds.SetMetadataItem('AREA_OR_POINT','Area','')
    # dst_ds.SetMetadataItem('TIFFTAG_RESOLUTIONUNIT', '1 (unitless)','')
    # dst_ds.SetMetadataItem('TIFFTAG_XRESOLUTION', '1','')
    # dst_ds.SetMetadataItem('TIFFTAG_YRESOLUTION', '1','')
  
    ds = None
    
#%%
if __name__ == "__main__":
    # Example:
    # netcdf_file = 'nas-chl-anomaly_w_08-28Mar-03Apr.nc'
    
    
    if len(sys.argv) != 2:
        print('Use: python nc2tiff.py [nc input file]')
        exit()
        
    netcdf_file = sys.argv[1]
    export_geotiff(netcdf_file)
