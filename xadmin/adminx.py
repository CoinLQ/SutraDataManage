from __future__ import absolute_import
import xadmin
from .models import UserSettings, Log
from xadmin.layout import *

from django.utils.translation import ugettext_lazy as _, ugettext
from .models import EmailVerifyRecord
from xadmin import views

from django.core.exceptions import PermissionDenied
from xadmin.views.base import filter_hook,BaseActionView
from xadmin.util import model_format_dict, model_ngettext
class UserSettingsAdmin(object):
    model_icon = 'fa fa-cog'
    hidden_menu = True

xadmin.site.register(UserSettings, UserSettingsAdmin)

class LogAdmin(object):

    def link(self, instance):
        if instance.content_type and instance.object_id and instance.action_flag != 'delete':
            admin_url = self.get_admin_url('%s_%s_change' % (instance.content_type.app_label, instance.content_type.model), 
                instance.object_id)
            return "<a href='%s'>%s</a>" % (admin_url, _('Admin Object'))
        else:
            return ''
    link.short_description = ""
    link.allow_tags = True
    link.is_column = False

    list_display = ('action_time', 'user', 'ip_addr', '__str__', 'link')
    list_filter = ['user', 'action_time']
    search_fields = ['ip_addr', 'message']
    model_icon = 'fa fa-cog'

xadmin.site.register(Log, LogAdmin)


 
class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']
 
xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True
 
xadmin.site.register(views.BaseAdminView, BaseSetting)

class GlobalSetting(object):
    site_title = "Sutra后台管理系统"
    site_footer = "longquan.AIITC"
 
xadmin.site.register(views.CommAdminView, GlobalSetting)

class zabbixitmes_display_off_action(BaseActionView):
    action_name = "zabbixitmes_display_off_action"
    description = u'%(verbose_name_plural)s 展示和采集关闭'
    model_perm = 'change'
 
    @filter_hook
    def change_models(self, queryset):
        n = queryset.count()
        if n:
            self.log('change', (u' %(count)d %(items)s. 展示和采集关闭')
                     % {"count": n, "items": model_ngettext(self.opts, n)})
            for obj in queryset:
                obj.display_insert = 0
                obj.save()
 
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        if self.request.POST:
            self.change_models(queryset)
            return None
    def DeleteSelectedAction(self, queryset):
        n = queryset.count()
        if n:
            self.log('change', (u' %(count)d %(items)s. 展示和采集关闭')
                     % {"count": n, "items": model_ngettext(self.opts, n)})
            for obj in queryset:
                obj.display_insert = 0
                obj.delete()