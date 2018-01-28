from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sutradata.models import *
from tasks.models import *
from django.db.utils import IntegrityError


import TripitakaPlatform.settings

import os, sys
from os.path import isfile, join
import traceback

from difflib import SequenceMatcher
import re, json
import xlrd

def myTestprint(info):
    # try:
    #     print(info)
    # except:
    #     print('myprintError.')
    return

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
    #FUNC_0  handle
    def handle(self, *args, **options):
        BASE_DIR = settings.BASE_DIR    
        
        #导入龙泉经目 OK            
        #self.ImportLQSutra()

        # print( self.getLQSutraID('0234'))
        # print( self.getLQSutraID('0234-23'))
        # print( self.getReelSutraID('LC1234'))
        # print( self.getReelSutraID('LC1234-23'))
        

        # #1) call 获得或创建管理员  OK
        # admin= self.CreateAdmin()

        #导入经目  OK
        #self.ImportSutraInfo()

        #导入卷    ok
        self.ImportSutraJuan()

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
                             

    #FUNC_1 CreateAdmin 获得或创建管理员
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

    #ImportSutraJuan 导入详目    
    # 1           2           3           4           5       6           7           8      9       
    # 龍泉編碼	高麗編碼	實體經名	    卷序號	    起始冊碼	起始頁碼	終止頁碼	終止冊碼	備註
    # LQ0246	GL0001	 大般若波羅蜜多經	0	      1	        1	      2	           1	    序
    #sutra = '实体藏经',           第二列
    #reel_no =                    第四列
    #start_vol = ('起始册')        第五列
    #start_vol_page = ('起始页')   第六列
    #end_vol = '终止册')           第八列
    #end_vol_page = ('终止页')     第七列
    def ImportSutraJuan(self):                 
        BASE_DIR = settings.BASE_DIR
        sutra_libs_file = '/data/sutra_text/xiangmu'        
        jingmufils=self.myEachFiles(BASE_DIR+sutra_libs_file)
        Reel.objects.all().delete()

        # load data
        for oneSutraFile in jingmufils :
            print (oneSutraFile)
            data = xlrd.open_workbook(oneSutraFile)
            table = data.sheets()[0]
            nrows = table.nrows
            ncols = table.ncols
            errorlist=[]
            #解析属性       
            pre_sutra_sid=''
            sutra=None
            for i in range(nrows):
                if i >0 and i<8  :
                    try:
                        sutra_sid=''
                        reel_no=-1
                        start_vol=-1
                        start_vol_page=-1
                        end_vol=-1
                        end_vol_page=-1                    
                        errMsg=''

                        myTestprint(i)
                        values = table.row_values(i)  
                        myTestprint(values)                                            
                        #sutra_sid = '实体藏经的id',           第二列                        
                        if len( str(values[1]) .strip() )<3 :#经号 #先处理经号不存在的情况
                            sutra=None
                            myTestprint ("1")
                            if  len( str(values[2]).strip() )>3 :# 看经名是否存在
                                myTestprint ("2")
                                #try:                                        
                                s=Sutra.objects.filter(name=str(values[2]).strip())  
                                if (len(s)>0):
                                    sutra=s[0]
                                    errMsg+='存疑G。经号不存在，通过经名搜索的第一个经。@行号'+str(i+1)   
                                myTestprint ("3")
                                #except:
                                myTestprint ("3.5")
                                #pass
                            if (sutra == None):# 都不存在，就跳过，记录日志。
                                myTestprint ("4")
                                a=("log: "+str(values[1])+":"+str(values[2])+":"+str(values[3])+":"
                                          +str(values[4])+":"+str(values[5])+":"+str(values[6]) +'errMsg:经名经号都异常，无法录入系统。@行号：'+str(i+1))                    
                                print(a)                                           
                                errorlist.append(a)   
                                continue
                            else:
                                sutra_sid=sutra.sid
                                myTestprint ("5")
                        else:                                    
                            sutra_sid=self.getReelSutraID( str(values[1]) ) #经编号  
                            myTestprint ("6")

                        myTestprint(sutra_sid)                                                                    
                        if not (pre_sutra_sid == sutra_sid)  :  
                            pre_sutra_sid=sutra_sid          
                            try :              
                                s=Sutra.objects.filter(sid=sutra_sid)#如果经号不存在情况这里有些冗余，但不影响效率。
                                if (len(s)>0):
                                    sutra=s[0]
                                myTestprint ("7")
                            except:#异常处理，经目缺少数据的。
                                tripitaka_id=sutra_sid[0:2]  
                                try :                      
                                    s=Tripitaka.objects.filter(code=tripitaka_id)
                                    if (len(s)>0):
                                        tripitaka=s[0]
                                except:
                                    pass
                                sutra = Sutra(sid=sutra_sid, name=str(values[2]),tripitaka=tripitaka
                                        , comment='@@@存疑E。经目数据缺失，从详目补充。@行号：'+str(i+1) , )                       
                                sutra.save()        
                                myTestprint ("8")
                            myTestprint(sutra)
                          
                        #['', 'QS0001', '大般若波羅蜜多經', 502.0, 10.0, 634.0, 10.0, '缺頁', '缺頁', '']
                        #reel_no =                    第四列
                        myTestprint( values[3])
                        if self.isCanGetNum( values[3]): #卷序号                             
                            reel_no=int(values[3])
                        else:
                            errMsg+='存疑F。第3列：['+str(values[3])+']不是一个数字。'
                        myTestprint('reel_no:'+ str(values[3] ) )
                        
                        #start_vol = ('起始册')        第五列                        
                        if self.isCanGetNum(values[4]) :
                            start_vol=int(values[4])
                        else:
                            errMsg+='存疑F。第4列：['+str(values[4])+']不是一个数字。'
                         #start_vol_page = ('起始页')   第六列
                        if self.isCanGetNum(values[5]) :
                            start_vol_page=int(values[5])
                        else:
                            errMsg+='存疑F。第5列：['+str(values[5])+']不是一个数字。'                            
                        myTestprint('start_vol_page:'+str(values[5]))
                        
                        #end_vol = '终止册')           第八列                                                
                        if self.isCanGetNum(values[7]) :
                            end_vol=int(values[7])                        
                        else:
                            errMsg+='存疑F。第7列：['+str(values[7])+']不是一个数字。'                                                        
                        myTestprint('end_vol:'+str(values[7]))
                       
                        #end_vol_page = ('终止页')     第七列  
                        if self.isCanGetNum(values[6]) :
                            end_vol_page=int(values[6])                                                                        
                        else:
                            errMsg+='存疑F。第6列：['+str(values[6])+']不是一个数字。'                                                        
                        myTestprint('end_vol_page:'+str(values[6]))

                        myTestprint(sutra)
                        myTestprint(reel_no)
                        myTestprint(start_vol)
                        myTestprint(start_vol_page)
                        myTestprint(end_vol)
                        myTestprint(end_vol_page)
                        reel = Reel(sutra=sutra,reel_no=reel_no, start_vol=start_vol,start_vol_page=start_vol_page
                                        , end_vol= end_vol, end_vol_page=end_vol_page,comment=errMsg )                       
                        reel.save()
                        if (len(errMsg)>0):
                            a=("log: "+str(i+1)+":"+sutra_sid+":"+str(reel_no)+":"+str(start_vol)+":"
                                          +str(start_vol_page)+":"+str(end_vol)+":"+str(end_vol_page) +'errMsg:'+errMsg)                    
                            myTestprint(a)                                          
                            errorlist.append(a)                                                                                      

                        myTestprint('end')
                    except IntegrityError as e:
                        errMsg='经号+卷号重复，无法导入此记录。'
                        a=("error: "+str(i+1)+":"+sutra_sid+":"+str(reel_no)+":"+str(start_vol)+":"
                                          +str(start_vol_page)+":"+str(end_vol)+":"+str(end_vol_page) +'errMsg:'+errMsg)
                        print(a)                                          
                        errorlist.append(a)
                    except :  
                        a=("error: "+str(i+1)+":"+sutra_sid+":"+str(reel_no)+":"+str(start_vol)+":"
                                          +str(start_vol_page)+":"+str(end_vol)+":"+str(end_vol_page) +'errMsg:'+errMsg)
                        print(a)                                          
                        errorlist.append(a)  
                    #break                     
            #break        
        
            #ll=[]       
            #             ll.append(l)
            # #print(ll)
            fl=open(oneSutraFile+'.log', 'w')
            for s in errorlist:
                fl.write(s)
                fl.write("\n")
            fl.close()
            #break
        return #ll
        pass

   #FUNC_2 ImportSutraInfo 导入经目
    #class Sutra(models.Model, TripiMixin):
    # lqsutra       对应模板第一列
    # sid =         对应模板第二列    
    # tripitaka     对应模板第二列，要解析前两位
    # variant_code  对应模板第二列，要解析横杠后面
    # name          对应模板第三列
    # total_reels   对应模板第四列
    # comment       对应模板第九列    
    def ImportSutraInfo(self):                   
        BASE_DIR = settings.BASE_DIR
        sutra_libs_file = '/data/sutra_text/jingmu'        
        jingmufils=self.myEachFiles(BASE_DIR+sutra_libs_file)
        Sutra.objects.all().delete()
        
        errorlist=[]
        # load data
        for oneSutraFile in jingmufils :
            print (oneSutraFile)
            errorlist.append(oneSutraFile)
            data = xlrd.open_workbook(oneSutraFile)
            table = data.sheets()[0]
            nrows = table.nrows
            ncols = table.ncols
            tripitaka_id=''#藏只有一次
            #解析属性           
            for i in range(nrows):
                if i >0  :
                    try:      
                        errMsg=''                  
                        lqsutra_id=''
                        sid=''                        
                        varindex=-1
                        variant_code=''
                        name=''
                        total_reels=-1
                        comment=''                        
                        values = table.row_values(i)                        
                        
                        sid=str(values[1])#  经ID                       
                        name=str(values[2]) #name          对应模板第三列
                        if (   len(name.strip()) <2 ):
                            errMsg+='存疑A。 经名存在异常。name:'+name+'。'  
                        # lqsutra       对应模板第一列
                        lqsutra_id=str(values[0]) #经编号  
                        #print(lqsutra_id)
                        #print("1.6")
                        if (len(lqsutra_id)<6 ): # 空编号
                            errMsg+='存疑C。龙泉编号不存在：'+lqsutra_id
                            lqsutra=None
                        else:           
                            lqsutra_id=self.getReelSutraID(str(values[0])) #经编号      
                            #print(lqsutra_id)             
                            #lqsutra_id=lqsutra_id[0:2]+"00"+lqsutra_id[2:]                                                        
                            try :
                                lqsutra=LQSutra.objects.get(sid=lqsutra_id.strip())
                            except:                        
                                lqsutra=None
                                errMsg+='存疑C。龙泉编号不存在：'+lqsutra_id                                                                            
                       
                        # sid =         对应模板第二列                          
                        if ( len ( sid.strip())<3    ):
                            errMsg+='存疑B。经编号在异常。id：'+sid+' 。'  
                        else:    
                            sid=self.getReelSutraID(str(values[1])) #经编号                                                                              
                            # tripitaka     对应模板第二列，要解析前两位
                            if len(tripitaka_id)== 0 :
                                tripitaka_id=sid[0:2]  
                                try :                      
                                    tripitaka=Tripitaka.objects.get(code=tripitaka_id)
                                except:
                                    pass                                                    
                            variant_code=varindex=sid[-1]# variant_code  对应模板第二列，要解析横杠后面

                            #查看经号是否重复
                            if len( Sutra.objects.filter(sid=sid)) >0 :
                                errMsg+='存疑D。经编号重复：'+sid    

                        mytotal_reels=values[3]
                        try :                            
                            total_reels=int(mytotal_reels)
                        except:
                            pass
                      
                        # comment       对应模板第九列
                        try :
                            comment=str(values[8])
                            if comment== None:
                                comment=""                                                             
                        except:
                            pass   
                        if (len(errMsg)>0):                                                        
                            a=("\nlog: "+str(i+1)+":"+str(values[0])+":"+str(values[1])+":"+str(values[2])+":"+str(values[3])+".errmsg:@@@"+errMsg)                    
                            #print(a)
                            comment+='@@@'+errMsg+'@行号：'+str(i+1)+'。'
                            errorlist.append(a)
                        # print(lqsutra_id)
                        # print(lqsutra)
                        # print(sid)
                        # print(name)
                        # print(variant_code)
                        # print("total_reels"+str(total_reels))
                        # print('comment:'+comment)      
                        # print('tripitaka:'+tripitaka.code)                                           
                        sutra = Sutra(sid=sid,lqsutra=lqsutra, name=name,tripitaka=tripitaka
                                        , variant_code= variant_code, total_reels=total_reels
                                        , comment=comment , code ='')                       
                        sutra.save()                        
                    except:
                        a=("error: "+str(i+1)+":"+str(values[0])+":"+str(values[1])+":"+str(values[2])+":"+str(values[3])+".errmsg:"+errMsg)                    
                        print(a)
                        errorlist.append(a)
                        # break
                        # pass
                    #break  
            fl=open(oneSutraFile+'.log', 'w')
            for s in errorlist:
                fl.write(s)
                fl.write("\n")
            fl.close()    
            errorlist.clear()
            #break                            
        return #ll
        pass

    #龙泉经编号的转化 excel文件导入的为四位或者5～6位，要规范为系统的8位
    #用户数据是 四位编码 & '-' & 别本号，转化为6位编号，前面加一个0，后面加一位别本号  (0~9a~z)  
    #用户数据 like '0123', or '0123-12' -的后面是别本号                   
    def getLQSutraID(self,orignid):                  
        hgindex=orignid.find('-') 
        nbiebenhao=0
        if hgindex ==4 :#带有横杠的
            nbiebenhao=int(orignid[5:]) 
        if (nbiebenhao<=9):
            id='LQ0'+orignid[0:4]+chr(nbiebenhao+48)
        else:
            id='LQ0'+orignid[0:4]+chr(nbiebenhao+97-10)                
        return id
    
    #转化整形值
    def isCanGetNum(self,value):         
        try :
            n=int(value)
            return True
        except:
            return False

    #实体藏经编号的转化 excel文件导入的为6位，要规范为系统的8位
    #用户数据是 四位编码 & '-' & 别本号，转化为6位编号，前面加一个0，后面加一位别本号  (0~9a~z)  
    #用户数据 like '0123', or '0123-12' -的后面是别本号                   
    def getReelSutraID(self,orignid):                  
        hgindex=orignid.find('-') 
        nbiebenhao=0
        if hgindex ==6 :#带有横杠的
            nbiebenhao=int(orignid[7:]) 
        if (nbiebenhao <= 9 ) :
            id=orignid[0:2]+'0'+orignid[2:6]+chr(nbiebenhao+48)
        else:
            id=orignid[0:2]+'0'+orignid[2:6]+chr(nbiebenhao+97-10)                
        return id

    #FUNC_3 ImportLQSutra 创建龙泉藏经 龙泉经目 第一个需求
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
        for i in range(nrows):
            if i>0 :
                values = table.row_values(i)                               
                sname=values[1]#经名
                nvolumns =1
                id=''
                try:
                    id= self.getLQSutraID( str(values[0]) )#转化编号
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

    #遍历文件夹，获取所有xls文件名
    def myEachFiles(self,path):
        _pathList=[]
        filepath = path
        
        fileTypes = ['.xlsx','.xls']
        
        if os.path.isdir(filepath):
            pathDir =  os.listdir(filepath)
            
            for allDir in pathDir:
                child = os.path.join('%s/%s' % (filepath, allDir))
                if os.path.isdir(child):
                    _pathList.append(myEachFiles(child))
                    pass
                else:
                    typeList = os.path.splitext(child)
                    if typeList[1] in fileTypes:#check file type:.txt
                        _pathList.append(child)
                        #print('child:','%s' % child.encode('utf-8','ignore'))
                        pass
                    else:#not .txt
                        pass
                
            pass
        else:
            typeList = os.path.splitext(filepath)
            if typeList[1] in fileTypes:#check file type:.txt
                _pathList.append(filepath)
                pass                            
            #print ('---',child.decode('cp936') )# .decode('gbk')是解决中文显示乱码问题
        #print(_pathList)    
        return _pathList  


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

    

    #comment 2018-1-25
    # def CreateLQSutra(self):        
    #     lqsutra=None
    #     strsid='LQ003100'
    #     try :            
    #         lqsutra = LQSutra.objects.get(sid=strsid) 
    #     except LQSutra.DoesNotExist:  
    #         print("藏经不存在 ID："+strsid)

    #     if (lqsutra):
    #         print("已经存在藏经 ID:"+strsid)            
    #     else:                             
    #         lqsutra = LQSutra(sid=strsid, name='大方廣佛華嚴經', total_reels=60)    
    #         print("创建华严经 ID："+strsid)
    #     lqsutra.save() 
    #     return lqsutra 


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


 
            


