#!/usr/bin/env python
# coding: utf-8
import cv2
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from os import listdir
from os.path import isfile, join
import sys

default_penalty=1.

import pytesseract as pts
pts.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"

def prepare_image(filename):
    img = cv2.imread(filename)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    # Цвет КП ММБ
    new_image = ((img[:,:,0] == 255) & (img[:,:,1] == 34) & (img[:,:,2] == 141) )*255
    new_image = new_image.astype(np.uint8)
    return new_image

def parse(new_image,circles):
    rows = []
    for i,circle in enumerate(circles[0]):
        x = int(circle[0])
        y = int(circle[1])
        radius = circle[2]

        delta = 140
        y1 = max(y-delta,0)
        y2 = min(y+delta,new_image.shape[0])
        x1 = max(x-delta,0)
        x2 = min(x+delta,new_image.shape[1])
        temp_img = new_image[y1:y2,x1:x2]
        temp_img = 255 - temp_img

        new_center_y = y-y1
        new_center_x = x-x1

        delta_r = 5
        max_r = 130

        x_coord = x
        y_coord = y
        #print (temp_img.shape,x_coord,y_coord,x1,x2,new_image.shape,y1,y2)

        for x in range(temp_img.shape[0]):
            for y in range(temp_img.shape[1]):
                dist = np.sqrt(pow((x-new_center_y),2) + pow((y-new_center_x),2))
                if (dist<radius+delta_r) and (dist>radius-delta_r): #это круг, убираем
                    temp_img[x,y]=255
                if (dist>max_r):
                    temp_img[x,y]=255
                            
        result = pts.image_to_string(temp_img,config='--psm 10 -c tessedit_char_whitelist=0123456789')

        result_digits = ''.join(filter(lambda x: x in '1234567890',result))

        cv2.imwrite('results/%d(%s).png'%(i,result_digits),temp_img)

        rows.append([x_coord,y_coord,radius,result,result_digits])
    result = pd.DataFrame(rows,columns = ['x','y','radius','text','text_digits'])
    return result

def find_kp(filename):
    img = prepare_image(filename)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 15,
                               param1=100, param2=15,
                               minRadius=24, maxRadius=35)
    df = parse(img,circles)
    df['penalty'] = default_penalty
    return df,circles

def plot_circles_on_img(filename,circles):
    img = cv2.imread(filename)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    if circles is not None:
        
        #print (circles.shape)
        for _,row in circles.iterrows():
            center = (row.x, row.y)
            # circle center
            cv2.circle(img, center, 1, (0, 255, 0), 3)
            # circle outline
            radius = int(row.radius)
            cv2.circle(img, center, radius, (0, 255, 0), 3)
            
            #print KP num
            font                   = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = center
            fontScale              = 1
            fontColor              = (0,0,0)
            lineType               = 3

            cv2.putText(img,row.text_digits, 
                bottomLeftCornerOfText, 
                font, 
                fontScale,
                fontColor,
                lineType
                       )
    return img


# path = 'maps/2019o'
# onlyfiles = [join(path,f) for f in listdir(path) if (isfile(join(path, f)) and f[-4:] != '.dat')]
# onlyfiles.sort()


# # In[47]:


# onlyfiles


# # In[71]:


# #map_file = 'maps/mmb2016o-l1.png'
# data = []
# for filename in onlyfiles:
#     print (filename)
#     points,circles = find_kp(filename)
#     data.append([filename,points,circles])
#     points.to_csv(filename+'.dat',index=False)

# img_test = data[map_id][0]

# img_for_plot = plot_circles_on_img(img_test,data[map_id][1])

# plt.figure(figsize=(24,24))
# plt.imshow(img_for_plot,cmap='gray')
# plt.connect('button_press_event',on_mouse_move)
# plt.show()


# In[19]:


# get_ipython().run_line_magic('matplotlib', 'notebook')
# import numpy as np
# import matplotlib.pyplot as plt
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot(np.random.rand(10))
# text=ax.text(0,0, "", va="bottom", ha="left")

def usage():
    print ('prepare_map.py <input_map.png>(jpg,gif) <modified_map> <output_data>')

if __name__ == '__main__':
    if len(sys.argv)<4:
        usage()
        sys.exit(1)
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    output_datafile = sys.argv[3]
    points,circles = find_kp(input_filename)
    points.to_csv(output_datafile,index=False)
    img_new = plot_circles_on_img(input_filename,points)
    #TODO save image
    img_new = cv2.cvtColor(img_new,cv2.COLOR_BGR2RGB)
    cv2.imwrite(output_filename, img_new)






