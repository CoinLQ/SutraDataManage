from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sutradata.models import *
from tasks.models import *

import TripitakaPlatform.settings

import os, sys
from os.path import isfile, join
import traceback

from difflib import SequenceMatcher
import re, json
import xlrd

def generate_compare_reel(text1, text2):
    """
    用于文字校对前的文本比对
    text1是基础本，不包含换行符和换页标记；text2是要比对的版本，包含换行符和换页标记。
    """
    SEPARATORS = re.compile('[p\n]')
    text2 = SEPARATORS.sub('', text2)
    diff_lst = []
    base_pos = 0
    pos = 0
    opcodes = SequenceMatcher(None, text1, text2, False).get_opcodes()
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            base_pos += (i2 - i1)
            pos += (i2 - i1)
        elif tag == 'insert':
            base_text = ''
            #if text2[j1] == '\n' and i1 > 0 and j1 > 0 and text1[i1-1] == text2[j1-1]:
            #    diff_lst.append( (2, base_pos, text1[i1-1], text2[j1-1:j2]) )
            #else:
            diff_lst.append( (2, base_pos, pos, base_text, text2[j1:j2]) )
            pos += (j2 - j1)
        elif tag == 'replace':
            diff_lst.append( (3, base_pos, pos, text1[i1:i2], text2[j1:j2]) )
            base_pos += (i2 - i1)
            pos += (j2 - j1)
        elif tag == 'delete':
            if base_pos > 0 and i1 > 0:
                diff_lst.append( (1, base_pos-1, pos-1, text1[i1-1:i2], text2[j1-1:j1]) )
            else:
                diff_lst.append( (1, base_pos, pos, text1[i1:i2], '') )
            base_pos += (i2 - i1)
    return diff_lst

#
#入口类
#
class Command(BaseCommand):
    #FUNC_1  handle
    def handle(self, *args, **options):
        BASE_DIR = settings.BASE_DIR        
        self.ImportLQSutra()
        # #1) call 获得或创建管理员
        # admin= self.CreateAdmin()

        # #2)  create LQSutra 创建龙泉经名 仅仅是名字
        # lqsutra = self.CreateLQSutra() 

        # #3)  create Sutra 创建某个版本的佛经对象  
        # #GL = Tripitaka.objects.get(code='GL')
        # #huayan_gl = Sutra(sid='GL000800', tripitaka=GL, code='00080', variant_code='0',
        # #name='大方廣佛華嚴經', lqsutra=lqsutra, total_reels=60)        
        # bandCode='GL'
        # strsid='GL000800'
        # code='00080'
        # var_code='0'
        # sname='大方廣佛華嚴經'
        # t_reels=60
        # huayan_yb=self.CreateSutra(bandCode,strsid,code,var_code,sname,lqsutra,t_reels)   

        #4)循环依次创建经卷
        #self.ImportSutraText(huayan_yb)
        return
                             

    #FUNC_2 CreateAdmin 获得或创建管理员
    def CreateAdmin(self):
        admin=None
        try :            
            admin = User.objects.get_by_natural_key('admin') 
        except User.DoesNotExist:  
            print("查询用户错误")

        if (admin):
            print("已经存在admin用户了")            
        else:                             
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'longquan')
            print("创建admn用户")
        return admin
    
    #FUNC_3 LQSutra 创建龙泉藏经 经名
    def CreateLQSutra(self):        
        lqsutra=None
        strsid='LQ003100'
        try :            
            lqsutra = LQSutra.objects.get(sid=strsid) 
        except LQSutra.DoesNotExist:  
            print("藏经不存在 ID："+strsid)

        if (lqsutra):
            print("已经存在藏经 ID:"+strsid)            
        else:                             
            lqsutra = LQSutra(sid=strsid, name='大方廣佛華嚴經', total_reels=60)    
            print("创建华严经 ID："+strsid)
        lqsutra.save() 
        return lqsutra 

        #FUNC_3 ImportLQSutra 创建龙泉藏经 经名
        # 4169 4692 开始不连续了
    def ImportLQSutra(self):       
        lqsutra=None
        #清空
        LQSutra.objects.all().delete() 
        #从excel中读取
        BASE_DIR = settings.BASE_DIR
        sutra_libs_file = 'data/sutra_text/LQBM.xls' #龙泉编码文件
        
        # load data
        data = xlrd.open_workbook(sutra_libs_file)
        table = data.sheets()[0]
        nrows = table.nrows
        ncols = table.ncols

        #解析属性
        properties = table.row_values(0)
        resultDatas = list()
        for i in range(nrows):
            if i>0 :
                values = table.row_values(i)
                id='LQ00'+str(values[0]) #经编号
                sname=values[1]#经名
                nvolumns =1
                try:
                   
                    if len(str(values[3]).strip())==0:
                        nvolumns=0
                    else:                                           
                        nvolumns= int (values[3])#卷数                    
                    lqsutra = LQSutra(sid=id, name=sname, total_reels=nvolumns )                       
                    lqsutra.save()
                except:
                    print('error j='+str(i)+'value:'+str(values[3])+'::'+id+sname+str(nvolumns))
                    pass                   
        # strsid='LQ003100'
        # try :            
        #     lqsutra = LQSutra.objects.get(sid=strsid) 
        # except LQSutra.DoesNotExist:  
        #     print("藏经不存在 ID："+strsid)

        # if (lqsutra):
        #     print("已经存在藏经 ID:"+strsid)            
        # else:                             
        #     lqsutra = LQSutra(sid=strsid, name='大方廣佛華嚴經', total_reels=60)    
        #     print("创建华严经 ID："+strsid)
        # lqsutra.save() 
        return   

    #FUNC_4 LQSutra 创建某个版本的佛经
    def CreateSutra(self,bandCode,strsid,code,var_code,sname,lqsutra,t_reels):  
        BASE_DIR = settings.BASE_DIR
        #取版本号
        Band = Tripitaka.objects.get(code=bandCode)#YB = Tripitaka.objects.get(code='YB')
        if (Band == None): 
            return
        #查看是否已经创建
        #下面的变量名要改的
        huayan_yb = None
        try :            
            huayan_yb = Sutra.objects.get(sid=strsid) 
        except Sutra.DoesNotExist:  
            print("版本["+bandCode+"]藏经不存在 ID："+strsid)

        if (huayan_yb):
             print("版本["+bandCode+"]藏经存在 ID："+strsid)
        else:
            huayan_yb = Sutra(sid=strsid, tripitaka=Band, code=code, variant_code=var_code,
                        name=sname, lqsutra=lqsutra, total_reels=t_reels)
            huayan_yb.save()
        return huayan_yb   
        pass   

    #Func_5  GetJingMuData  返回值是list嵌套 
    def GetJingMuData(self, ):                              
        BASE_DIR = settings.BASE_DIR
        sutra_libs_file = 'data/sutra_text/gl_hyj60.csv' #华严经60卷目录文件
        sutra_origin_sid='GL0080'

        #循环读取文件数据
        filename = os.path.join(BASE_DIR, sutra_libs_file)
        with open(filename,'r') as f:
            sutra_text = f.readlines()
        ll=[]
        for x in range(len(sutra_text)):
            line_text = sutra_text[x]
            line_list = line_text.split('\t')            
            if len(line_list) >= 7:
                if line_list[0] == sutra_origin_sid:#判断经目及其他条件
                    sid_list =list(line_list[0])
                    sid_list.insert(2,'0')
                    sid =''.join(sid_list)+'0'
                    sutra_name_text = line_list[1]
                    reel_no = int(line_list[2])
                    vol_no = int(line_list[3])
                    start_page_no = int(line_list[4])
                    end_page_no = int(line_list[5])
                    #缓存数据
                    l=[sid,sutra_name_text,reel_no,vol_no,start_page_no,end_page_no]
                    ll.append(l)
        #print(ll)
        return ll
        pass

    #Func_6  ImportSutra 导入经卷
    #先导入 高丽藏第一卷 为例
    #暂时不支持重复导入，还不知道Reel表是否可以支持关键字查询
    # def ImportSutraText(self, huayan_gl,):                                
    #     BASE_DIR = settings.BASE_DIR
    #     ll=self.GetJingMuData() #获得经目数据
    #     #huayan_gl_1 = Reel(sutra=huayan_gl, reel_no=1, start_vol=14,start_vol_page=31, end_vol=14, end_vol_page=37)

    #     #读取经文
    #     fullSutraText=''#全部经文
    #     OneVolumnText=''#某卷经文
    #     filename = os.path.join(BASE_DIR, 'data/sutra_text/%s_1.txt' % huayan_gl.sid)
    #     with open(filename, 'r') as f:
    #         sutraText = f.read()
        
    #     lines = sutraText.split('\n')#全部经文行列表
    #     prePageIndex=1
    #     preVolumnIndex=1
    #     for line in lines:     
    #         line=line.replace(' ','')                          
    #         if not (line.strip() ):#过滤空行
    #             continue

    #         print(line)
    #         arr=line.split(';')               
    #         #分卷
    #         i=arr[0].find('V')+1
    #         p= int ( arr[0][i:i+3])
    #         if (p>preVolumnIndex):     
    #             #
    #         print(arr)
    #         OneVolumnText=OneVolumnText+arr[1]+'\n'  
    #         #分页
    #         i=arr[0].find('P')+1
    #         p= int ( arr[0][i:i+2])
    #         if (p>prePageIndex):
    #             prePageIndex=p
    #             OneVolumnText=OneVolumnText+'p\n'              
    #     #huayan_gl_1.save()

        # 大藏经第 卷的文本
        #huayan_sutra_1 = Reel(sutra=huayan_gl, reel_no=reel_no, start_vol=vol_no,start_vol_page=start_page_no, end_vol=vol_no, end_vol_page=end_page_no)                    
        #huayan_sutra_1.text = get_reel_text(sid, reel_no, vol_no,start_page_no, end_page_no)
        #huayan_sutra_1.save()
        #print(line_list,line_list[3],huayan_sutra_1)
        #huayan_gl_1 = Reel(sutra=huayan_gl, reel_no=1, start_vol=14,start_vol_page=31, end_vol=14, end_vol_page=37)


 
            


