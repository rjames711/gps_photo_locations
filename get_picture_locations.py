# coding: utf-8
import os
import geopy.distance
from GPSPhoto import gpsphoto
import pyexifinfo as pe
import pickle
'''
location,coordinates, withinKM = 'boulderCo',(40.0150, -105.2705),200
location,coordinates, withinKM='Florida',(26.7153, -80.0534),200
location,coordinates, withinKM = 'williampenn', (39.6721327,-75.5896958),1
location,coordinates, withinKM= '400Anchormill', (39.6737515,-75.5599767),2
location,coordinates, withinKM= 'concordville', (39.8900351,-75.527584),2
'''

location,coordinates, withinKM='ardende',(39.8105697,-75.4968022),2

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
    #print(coord)
    deg = int(coord[0])
    #print(coord)
    minute = coord[2]
    #print(minute)
    minute = int(minute[0:len(minute)-1])
    sec = float(coord[3][0:5])
    #print(deg,minute,sec)
    DD = deg+(minute/60)+(sec/3600)
    return DD


paths = []


def traverse():
    for root, dirs, files in os.walk("..", topdown=False):
        for name in files:
            ext = name.split('.')
            ext = ext[len(ext)-1]
            if ext == 'jpg' or ext =='mp4':
                
                pwd = root.split('/')
                pwd = pwd[len(pwd)-1]
                if pwd == 'thumbnails':
                    continue
                #print('root:',root)
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
        print(afile)
        i+=1
        if afile in file_coords:
            coord = file_coords[afile]
            if coord == 'error':
                print('no gps')
                continue
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
                print('error reading gps')
                file_coords[afile] = 'error'
                continue
    pickle.dump(file_coords, open("coords.p","wb"))
    from pprint import pprint
    f=open('dump.txt','w')
    pprint(file_coords, stream=f)
    f.close()
    writeFile('last.out')

def clearFiles():
    f = open(location+str(withinKM)+'.csv', 'w')
    h = open(location+'-'+str(withinKM)+'km.html', 'w')
    f.close()
    h.close()

html = ''
csv = ''
fcount=0
def writeFile(afile):
    print(writeFile.fcount)
    writeFile.fcount+=1
    name = afile.split('/')
    name = name[len(name)-1]
    name = './thumbnails/'+name

    ext = afile.split('.')
    ext = ext[len(ext)-1]
    if ext == 'mp4':
        writeFile.html += '<video width="160" height="120" controls><source src="'+afile+'"type="video/mp4"></video>'
    else:
        exists = os.path.isfile(name)
        if not exists:
            try:
                print('writing thumbnail')
                im = Image.open(afile)
                size = 128, 128
                im.thumbnail(size)
                im.save(name)
            except:
                print('error writing thumbnail')
                
        writeFile.html += '<a href="'+afile+'" >'
        writeFile.html += '<img src="'+name+'" width="160" height="120">'
        writeFile.html += '</a>'
    writeFile.csv += afile+'\n'
    if writeFile.fcount == 100 or afile=='last.out':#last.out is stupid hack to get it to force to write out any remaining
        outf = location+'-'+str(withinKM)+'km.csv'
        outh = location+'-'+str(withinKM)+'km.html'
        #f = open('outf.csv', 'a')
        #h = open('outh.html', 'a')
        f = open(outf, 'a')
        h = open(outh, 'a')
        t = open('test.txt', 'a')

        t.write('test')
        f.write(writeFile.csv)
        h.write(writeFile.html)
        h.close()
        f.close()
        t.close()
        print('writing files', outf, outh)
        print(writeFile.html)
        writeFile.fcount = 0
        writeFile.html = ''
        writeFile.csv = ''
        
    closepaths.append(afile)
writeFile.fcount=0
writeFile.html = ''
writeFile.csv = ''

if __name__=="__main__":
    getWorkPicture()

