# coding: utf-8
import os
import geopy.distance
from GPSPhoto import gpsphoto
import pyexifinfo as pe
import pickle
'''

location = 'boulderCo'
coordinates = (40.0150, -105.2705)
'''

location = 'Newcastle'
coordinates = (39.6737515,-75.5599767)
withinKM = 100

def get_photo_coords(photo):
    data = gpsphoto.getGPSData(photo)
    coords = (data['Latitude'], data['Longitude'])
    return coords


def get_distance(c1, c2):
    return geopy.distance.distance(c1, c2).km


def getFileDistance(f1, f2):
    return get_distance(getFileCoord(f1), getFileCoord(f2))


def getFileCoord(afile):
    data = pe.get_json(afile)[0]
    lat = data['Composite:GPSLatitude']
    lon = data['Composite:GPSLongitude']
    print(lat, lon)
    return (convertGPStoFloat(lat), -convertGPStoFloat(lon))


def convertGPStoFloat(coord):
    coord = coord.split(' ')
    print(coord)
    deg = int(coord[0])
    print(coord)
    minute = coord[2]
    print(minute)
    minute = int(minute[0:len(minute)-1])
    sec = float(coord[3][0:5])
    print(deg,minute,sec)
    DD = deg+(minute/60)+(sec/3600)
    return DD


paths = []


def traverse():
    for root, dirs, files in os.walk("..", topdown=False):
        for name in files:
            ext = name.split('.')
            ext = ext[len(ext)-1]
            if ext == 'jpg':
                relpath = os.path.join(root, name)
                paths.append(relpath)
                # paths.append(os.path.abspath(relpath))


closepaths = []
file_coords = {}
from PIL import Image
def getWorkPicture():
    try:
        file_coords = pickle.load(open("coords.p","rb"))
    except:
        file_coords ={}
    traverse()
    clearFiles()
    i=0
    for afile in paths:
        i+=1
        if afile in file_coords:
            coord = file_coords[afile]
            if get_distance(coord, coordinates) < withinKM:
                writeFile(afile)
        else:
            try:
                coord = getFileCoord(afile)
                file_coords[afile] = coord
                #feh below
                if i%100 == 0:
                    print('pickling')
                    pickle.dump(file_coords, open("coords.p","wb"))
                if get_distance(coord, coordinates) < withinKM:
                    writeFile(afile)
            except:
                continue
    pickle.dump(file_coords, open("coords.p","wb"))

def clearFiles():
    f = open(location+str(withinKM)+'.csv', 'w')
    h = open(location+'-'+str(withinKM)+'km.html', 'w')
    f.close()
    h.close()

def writeFile(afile):
    name = afile.split('/')
    name = name[len(name)-1]
    name = './thumbnails/'+name
    f = open(location+'-'+str(withinKM)+'km.csv', 'a')
    h = open(location+'-'+str(withinKM)+'km.html', 'a')
    ext = afile.split('.')
    ext = ext[len(ext)-1]
    if ext == 'mp4':
        html = '<video width="320" height="240" controls><source src="'+afile+'"type="video/mp4"></video>'
    else:
        
        im = Image.open(afile)
        size = 128, 128
        im.thumbnail(size)
        im.save(name)
        html = '<a href="'+afile+'" >'
        html += '<img src="'+name+'" >'
        html += '</a>'
    afile += '\n'
    f.write(afile)
    h.write(html)
    h.close()
    f.close()
    closepaths.append(afile)


if __name__=="__main__":
    getWorkPicture()

