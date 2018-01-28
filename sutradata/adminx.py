import xadmin
from xadmin import views
from .models import LQSutra
from .models import Tripitaka
from .models import Sutra,Reel,Volume


#龙泉经目 LQSutra
class LQSutraAdmin(object):
    list_display = ['sid','name','total_reels','showSutra'] #自定义显示这两个字段
    def showSutra(self,obj) :              
        #xadmin/sutradata/sutra/?_q_=佛说阿弥陀经        
        return '<a href="/xadmin/sutradata/sutra/?_p_lqsutra__id__exact='+str(obj.id)+'">查看版本</a>'
        #return '<a href="/xadmin/sutradata/sutra/?">查看版本</a>'
    showSutra.short_description = u'操作'
    showSutra.allow_tags = True

    search_fields = ['sid','name']
    list_filter = ['sid','name']
    ordering = ['sid',] ##按照倒序排列  -号是倒序

#实体藏 Tripitaka
class TripitakaAdmin(object):
    list_display = ['id','name','code','operator'] #自定义显示这两个字段
    def operator(self,obj) :                              
        edit='<a href="/xadmin/sutradata/tripitaka/'+str(obj.id)+'/update/">修改</a> '
        dele='<a href="/xadmin/sutradata/tripitaka/'+str(obj.id)+'/delete/">删除</a> '
        return edit+dele    
    operator.short_description = u'操作'
    operator.allow_tags = True
    # search_fields = ['question_text','pub_date'] #可以搜索的字段
    # list_filter = ['question_text','pub_date']
    ordering = ['id',] ##按照倒序排列


#实体经  Sutra
class SutraAdmin(object):
    list_display = ['tripitaka','name','total_reels','Real_reels','sid','lqsutra_name','lqsutra_sid','comment','operator'] #自定义显示这两个字段     
    def Real_reels(self,obj) :           
        return Reel.objects.filter(sutra=obj.id).count() 

    def operator(self,obj) :                      
        edit='<a href="/xadmin/sutradata/sutra/'+str(obj.id)+'/update/">修改</a> '
        dele='<a href="/xadmin/sutradata/sutra/'+str(obj.id)+'/delete/">删除</a> '
        return edit+dele    
    operator.short_description = u'操作'
    operator.allow_tags = True

    def lqsutra_sid(self,obj) :   
        if obj == None : return
        line=obj.lqsutra.__str__()        
        line_list = line.split(':')      
        return line_list[0] 

    def lqsutra_name(self,obj) :              
        line=obj.lqsutra.__str__()        
        line_list = line.split(':')    
        if len(line_list) <2 :return
        return line_list[1]
    lqsutra_sid.short_description = u'龙泉编码'
    lqsutra_name.short_description = u'龙泉经名'
    Real_reels.short_description=u'实存卷数'
    list_select_related=False

    search_fields = ['name','lqsutra__id','sid'] #可以搜索的字段    
    free_query_filter=True
    list_filter =['name','lqsutra__id','sid'] 
    # ordering = ['-pub_date',] ##按照倒序排列    

class VolumeAdmin(object):
    list_display = ['tripitaka_name','vol_no','page_count'] #自定义显示这两个字段   
    def tripitaka_name(self,obj) : #藏名 
        t=Tripitaka.objects.get(code=obj.tripitaka.code)
        s=t.__str__()
        return t

class ReelAdmin(object):
    list_display = ['tripitaka_name','sutra_name','reel_no','start_vol','start_vol_page','end_vol','end_vol_page'
                    ,'edition_type','comment','status_1','status_2','status_3','status_4'] #自定义显示这两个字段    
    def tripitaka_name(self,obj) : #藏名 
        t=Tripitaka.objects.get(code=obj.sutra.tripitaka.code)
        s=t.__str__()
        return t
    def sutra_name(self,obj) :          
        return obj.sutra.name
    def status_1(self,obj):
        return 'x'
    def status_2(self,obj):
        return 'x'
    def status_3(self,obj):
        return 'x'
    def status_4(self,obj):
        return 'x'
    sutra_name.short_description = u'经名'
    tripitaka_name.short_description = u'藏名'
    status_1.short_description= u'数据总状态'
    status_2.short_description= u'图片状态'
    status_3.short_description= u'切分数据状态'
    status_4.short_description= u'识别数据状态'
    # search_fields = ['question_text','pub_date'] #可以搜索的字段
    # list_filter = ['question_text','pub_date']
    # ordering = ['-pub_date',] ##按照倒序排列    
 

#  class Reel2Admin(object):
#     list_display = ['tripitaka_name','sutra_name','reel_no','longquan_Name','edition_type','comment'] #自定义显示这两个字段    
#     def tripitaka_name(self,obj) : #藏名 
#         t=obj.lqsutra.name)        
#         return t

#     def longquan_Name(self,obj) : #藏名 
#         t=sutr.objects.get(code=obj.sutra.tripitaka.code)
#         s=t.__str__()
#         return t
#     def sutra_name(self,obj) :          
#         return obj.sutra.name
    
#     sutra_name.short_description = u'经名'
#     tripitaka_name.short_description = u'藏名'
#     longquan_Name.short_description=u'龙泉经名'

    # search_fields = ['question_text','pub_date'] #可以搜索的字段
    # list_filter = ['question_text','pub_date']
    # ordering = ['-pub_date',] ##按照倒序排列  
     
xadmin.site.register(LQSutra,LQSutraAdmin)
xadmin.site.register(Tripitaka,TripitakaAdmin)
xadmin.site.register(Volume,VolumeAdmin) 
xadmin.site.register(Sutra,SutraAdmin)
xadmin.site.register(Reel,ReelAdmin) 
#xadmin.site.register(ReelAdmin2) 

class GlobalSetting(object):
    site_title = '龙泉大藏经'   #设置头标题
    site_footer = '龙泉大藏经'  #设置脚标题
    menu_style = 'accordion'

xadmin.site.register(views.CommAdminView, GlobalSetting)