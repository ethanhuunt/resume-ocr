from django.shortcuts import render
from .models import Employees, Body, Info, Soldier
from PIL import Image
from django.core.files.storage import FileSystemStorage
import pytesseract
from .ocrtools.resume import naverclova
from .ocrtools.body import title_read



#------------------------------------------------------
# 병역문서 인식을 위해 필요한 import 들
from easyocr.easyocr import *
import cv2
import requests
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import os


import sys

import matplotlib.pyplot as plt
plt.style.use('seaborn-white')

from .ocrtools.armyOCR.easy.army import call_army
# -------------------------------------------------
# Create your views here.

def home(request):

    employees = Employees.objects.all()

    context = {
        'employees' : employees,
    }

    return render(request, 'index.html', context)



def result(request,i):

    msg = "정보를 불러올 수 없습니다."

    emp= Employees.objects.get(id=i)

    context = {
        'name':emp.name,
        'idx':i,
    }

    try:
        body = Body.objects.get(emp = i)
        info = Info.objects.get(emp = i)
        soldier = Soldier.objects.get(emp = i)

        context['body'] = body
        context['info'] = info
        context['soldier'] = soldier

    except Exception as e:

        context['msg'] = msg


    return render(request, 'result.html', context)

def ocr(request,i):
    print(i,'iiiii')
    paths=[]
    context = {}
    context['menutitle'] = 'OCR READ'
    
    context['imgname']=[]
    resulttext = ''
    context['idx']=i
    
    if 'uploadfile' in request.FILES:
        print(100)
        uploadfile = request.FILES.getlist('uploadfile', '')
        print(uploadfile)
        if uploadfile != '':
            for i in uploadfile:

                name_old = i.name
                
                fs = FileSystemStorage(location = 'static/source')
                imgname= fs.save(f'src-{name_old}', i)
                print(imgname)
                context['imgname'].append(imgname)
                imgfile = Image.open(f'./static/source/{imgname}') 
                path=f'./static/source/{imgname}'
                print(path)
                paths.append(path)
                
        
        result=naverclova(paths[1],paths[0])
        context['resulttext1']=result[0]
        context['resulttext2']=[]
        a=result[1:]
        
        for i in enumerate(a):
            
            context['resulttext2'].append(i)

        print(context['resulttext2'])
        context['first']=context['imgname'][0]
        context['remain']=context['imgname'][1:]
        context['len']=len(a)
        print(context['len'])

    return render(request,'ocr.html',context)





# -------------------------------------------------------------------------------

# 병역문서 불러오는 부분

def ocrarmy(request,i):
    context = {}
    print('jfj')
    print(i)
    print('ocrarmy')
    if 'uploadfile' in request.FILES:
        
        
        # uploadfile은 html에서 불러오는 것
        uploadfile = request.FILES.get('uploadfile', '')
        print(uploadfile)
        print('asdfljasdflkj')
            
        if uploadfile != '':
            name_old = uploadfile.name
            print('제발')


            # 이미지를 불러오는 경로도 좀 손을 봐야 한다
            

            #fs = FileSystemStorage(location = 'static\source\document_army')    # 이미지들이 저장되는 곳
            fs = FileSystemStorage(location = 'static/source/document_army')    # 이미지들이 저장되는 곳
            imgname= fs.save(f'src-{name_old}', uploadfile)       # 이미지를 저정하는 동작 (이미지명, 이미지파일)
            # print(imgname)                                        # 이미지명 확인


            #path=f'static\source\document_army'                   # 이미지를 불러올 경로
            path=f'static/source/document_army'                   # 이미지를 불러올 경로
            print(path)


            # ------------------------------------------------- 
            # 만들어둔 EasyOCR을 부르는 부분
            # subhap\ocrtools\armyOCR\easy 경로에서 army.py 에서 call_army를 호출 경로를 보내줌

            resulttext = call_army(path)    
            # resulttext = call_army(path, imgname)    

            # ---------------------------------------------------

        context['imgname'] = imgname
        context['resulttext'] = resulttext
    context['idx'] = i



    return render(request,'ocrarmy.html',context)



def ocrbody(request, i):
    context = {}
    context['idx'] = i
    context['imgname'] = []
    if 'uploadfile' in request.FILES:
        
        uploadfile = request.FILES.getlist('uploadfile', '')
            
        if uploadfile != '':
            for i in uploadfile:
                name_old = i.name
            
                fs = FileSystemStorage(location = 'static/source')
                imgname= fs.save(f'src-{name_old}', i)
                print(imgname)
                context['imgname'].append(imgname)
                imgfile = Image.open(f'./static/source/{imgname}')
                path=f'./static/source/{imgname}'

                resulttext = title_read(imgfile)
            #지금은 파이테서렉트 쓴것이 리절트 텍스트 
            #은수님의 모듈 결과를 resulttext에 대입해주세요
        
        
                context['resulttext'] = resulttext
        context['first']=context['imgname'][0]
        context['remain']=context['imgname'][1:]


        context['first']=context['imgname'][0]
        context['remain']=context['imgname'][1:]
    return render(request,'ocrbody.html',context)



# 신체정보 insert 함수
def insertBody(request, i):
    # 필요한 data = 사원ID, 키, 몸무게, 시력_(좌, 우), 지병

    height = request.POST.get('height')
    weight = request.POST.get('weight')
    eye_l = request.POST.get('eye_l')
    eye_r = request.POST.get('eye_r')
    disease = request.POST.get('disease')

    try:
        Body.objects.create(emp_id=i, height=height, weight=weight, eye_l=eye_l, eye_r=eye_r, disease=disease)
        print('body table에 insert')
    except Exception as e:
        print(e)

    context = {
        'idx' : i
    }

    return render(request, 'result.html', context)

def ocrresident(request,i):
    context = {}
    context['idx'] = i
    if 'uploadfile' in request.FILES:
        
        uploadfile = request.FILES.get('uploadfile', '')
            
        if uploadfile != '':
            name_old = uploadfile.name
            
            fs = FileSystemStorage(location = 'static/source')
            imgname= fs.save(f'src-{name_old}', uploadfile)
            print(imgname)
            imgfile = Image.open(f'./static/source/{imgname}')
            path=f'./static/source/{imgname}'
            #resulttext = pytesseract.image_to_string(imgfile, lang='kor')
            #지금은 파이테서렉트 쓴것이 리절트 텍스트 
            #혜지님의 모듈 결과를 resulttext에 대입해주세요
        resulttext='' 
        context['imgname'] = imgname
        context['resulttext'] = resulttext


    return render(request,'ocrbody.html',context)

def insertResume(request,i):
    # 필요한 data = 사원ID, 키, 몸무게, 시력_(좌, 우), 지병

    length = int(request.POST.get('len'))
    print(length)
    qual=[]
    gr=request.POST.get('gradu')
    for l in range(length):
        ja=request.POST.get('{}'.format(l))
        print(ja)
        qual.append(ja)

    try:
        Info.objects.create(emp_id=i,graduation=gr,license=qual)
        print('info table에 insert')
    except Exception as e:
        print(e)

    context = {
        'idx' : i
    }

    return render(request, 'result.html', context)
