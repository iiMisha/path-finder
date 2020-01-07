#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from tqdm import tqdm_notebook
import copy
from matplotlib import pylab as plt
import cv2
from os import path
import argparse
import json
import math
import io

# def getArrayFromPoint(points,text_name):
#     return points[points.text_digits==text_name][['x','y','radius','text_digits']].iloc[0].values
# def getArrayFromPoints(points):
#     return points[['x','y','radius','text_digits']].values

def getArrayFromPoint(points,text_name):
    return points[points.name==text_name][['lat','long','name','name']].iloc[0].values
def getArrayFromPoints(points):
    return points[['lat','long','name','name']].values

def route_dist(route):
    dist = start_distances[route[0]]
    for p1,p2 in zip(route[:-1],route[1:]):
        dist += distance_matrix[p1,p2]
    return dist + finish_distances[route[-1]]

def distance(x,y):
    return np.sqrt((float(x[0])-float(y[0]))**2  + (float(x[1])-float(y[1]))**2)

def distance(x,y): 
    lng_1, lat_1, lng_2, lat_2 = map(math.radians, [x[1], x[0], y[1], y[0]])
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1 

    temp = (  
         math.sin(d_lat / 2) ** 2 
       + math.cos(lat_1) 
       * math.cos(lat_2) 
       * math.sin(d_lng / 2) ** 2
    )

    return 6373.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))

def register_top(route,dist):
    global top
    global routes_to_find
    global porog
    top.append((points[route],dist))
    top = sorted(top,key = lambda x: x[1])[:routes_to_find]
    #print 'new top'
    try:
        last = top[routes_to_find-1]
        #print 'porog changed'
        porog = last[1]
    except:
        pass
    
def best_route(route,dist,verbose=True):
    current = route[-1]
    if dist+porog_adjust[len(points)-len(route)] > porog:
        return
    if dist+finish_distances[current]>porog:
        return
    if len(route) == len(points):
        register_top(route,dist+finish_distances[current])
        return
    points_walked = 0
    if (len(route)==4) and (verbose==True):
        print (points[route][:,3], top[0][1] if len(top)> 0 else 2000000000 )
    for i in sorted_by_distance_points[current]:
        if i in route:
            continue
        new_route = copy.copy(route)
        new_route.append(i)
        new_dist = dist+distance_matrix[current,i]
        if new_dist>porog:
            continue
        best = best_route(new_route,new_dist,verbose=verbose)
        points_walked+=1
        if points_walked == nearest_points:
            break

def kp_gen(kp_str):
    kp_strs = kp_str.split(',')
    for s in kp_strs:
        if '-' in s:
            v = s.split('-')
            min_s = int(v[0])
            max_s = int(v[1])
            for i in range(min_s,max_s+1,1):
                yield str(i)
        else:
            yield s

def print_top():
    best = top[0][1]
    res = ''
    for t in top:
        st = '[%s] %s (%s %s)' % (' '.join(np.concatenate([[start],t[0],[finish]])[:,3]), 
            '%.3f км'%(t[1]*factor), 
            '(-%.3f,'%((t[1]-best)*factor), 
            '%.2f%%)' % ((t[1]-best)*100./best))
        print (st)
        res += st+'\n'
    return res
        
def print_top_with_skipped():
    best = top[0][1]
    for t in top:
        st = '[%s] [%s] %s (%s %s)' %  (' '.join(np.concatenate([[start],t[0],[finish]])[:,3]),
            ' '.join((list(set(all_points[:,3]) - set(t[0][:,3]) - set([start[3],finish[3]])))),
            '%.3f км'%(t[1]*factor), 
            '(-%.3f,'%((t[1]-best)*factor), 
            '%.2f%%)' % ((t[1]-best)*100./best))

def save_top():
    for i,t in enumerate(top):
        new_image = copy.copy(img)
        route = np.vstack([[start],t[0],[finish]])
        for p1,p2 in zip(route[:-1],route[1:]):
            lineThickness = 7
            new_image = cv2.line(new_image, (p1[0], p1[1]), (p2[0], p2[1]), (255,0,0), lineThickness)
        filename = '%d. %s (%.3f km).jpg' % (i+1,'-'.join(np.concatenate([[start],t[0],[finish]])[:,3]),t[1]*factor)
        new_image = cv2.cvtColor(new_image,cv2.COLOR_RGB2BGR)
        cv2.imwrite(path.join(outfolder,filename), new_image)
    text_file = open(path.join(outfolder,'best_routes.txt'),'w')
    text_file.write(best_routes)
    text_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument("-m","--map", help="path to map file",required=True)
    parser.add_argument("-s","--start", help = "name of start point",required=True);
    parser.add_argument("-f","--finish", help="name of finish point",required=True)
    parser.add_argument( "--kps-in", help="list of KPs in scope of search (5,9-13,SK - possible format)",required=True)
    parser.add_argument("-d","--data", help="data filename (result of check_for_mistake.py)",required=True)
    #parser.add_argument("--mashtab",help = "mashtab of map",type=int)
    parser.add_argument("--routes-to-find",help = "number of routes to find",type=int,default=10)
    parser.add_argument("--neares-points",help = "nearest_points of each to check",type=int,default=8)
    parser.add_argument("--penalty-allowed",help = "penalty allowed (in hours) (doesn't support currently)",type=float,default=0.)
    parser.add_argument("--kps-to-skip", help = "number of KPs to skip without penalty",type=int,default=0)
    parser.add_argument("-o",'--out-folder', help = "folder to store top maps")
    args = parser.parse_args()

    start_name = args.start
    finish_name = args.finish
    kp_in = args.kps_in
    dat_filename = args.data
    #map_filename = args.map
    # mashtab  = args.mashtab
    nearest_points = args.neares_points
    routes_to_find = args.routes_to_find
    penalty_allowed = args.penalty_allowed
    kps_to_skip = args.kps_to_skip
    outfolder = args.out_folder

    # #factor = 1./((st_297/297)*mashtab/1000)
    # sms_per_pixel = 29.7/st_297
    # kms_per_pixel = mashtab*sms_per_pixel/100000
    # factor = kms_per_pixel

    factor = 1.

    #format data
    if dat_filename[-4:] == '.wpt':
        f = open(dat_filename)
        data = f.read()
        csv = '\n'.join(data.split('\n')[4:])
        test_file = io.BytesIO(csv.encode('ascii'))
        data = pd.read_csv(test_file,header=None)
        data.columns = ['-1','name','lat','long'] + [i for i in range(4,25)]
        data_new = data[['name','lat','long']]
        points = data_new
    else:
        points = pd.read_csv(dat_filename,header=0,dtype={'name':'str'})

    start = getArrayFromPoint(points,start_name)
    finish = getArrayFromPoint(points,finish_name)
    kps = list(kp_gen(kp_in))
    points = points[points.name.isin(kps)]
    points = getArrayFromPoints(points)
    all_points = np.concatenate(([start],points,[finish]))
    #prepare tables
    start_distances = np.array([distance(start,x) for x in points])
    points = points[start_distances.argsort()]
    start_distances = np.array([distance(start,x) for x in points])
    distance_matrix = np.array([[distance(x,y) for x in points] for y in points])
    finish_distances = np.array([distance(finish,x) for x in points])
    sorted_by_distance_points = [distance_matrix[i].argsort() for i in range(len(points))]

    nearest_peregons = distance_matrix.flatten()
    nearest_peregons = nearest_peregons[nearest_peregons!=0]
    nearest_peregons.sort()
    nearest_peregons = nearest_peregons[::2]
    nearest_peregons = nearest_peregons.cumsum()

    porog_adjust = np.hstack([np.array([finish_distances.min()]), nearest_peregons+finish_distances.min()])

    #work
    top = []
    porog=1e20
    if kps_to_skip == 0:
        for first in (range(len(points))):
            b = best_route([first],start_distances[first],verbose=False)
    else:
        all_best = []
        for combination in (itertools.combinations(range(1,len(kps),1),len(kps)-kps_to_skip)):
            points_ind = np.concatenate((combination,))
            points = all_points[points_ind]
            distance_matrix = np.array([[distance(x,y) for x in points] for y in points])
            start_distances = np.array([distance(start,x) for x in points])
            finish_distances = np.array([distance(finish,x) for x in points])
            sorted_by_distance_points = [distance_matrix[i].argsort() for i in range(len(points))]
            for first in range(len(points)):
                b = best_route([first],start_distances[first],verbose=False)   

    print ("Top routes:")
    if kps_to_skip == 0:
        best_routes = print_top()
    else:
        best_routes = print_top_with_skipped()
    if outfolder is not None:
        print ("Saving top maps and routes to %s" % outfolder)
        save_top()

