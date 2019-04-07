# -*- coding: utf-8 -*-
#
import re
from wechat.models import *
from wechat.wrapper import WeChatHandler
from wechat.views import CustomWeChatView
from django.db.transaction import TransactionManagementError
from django.core.exceptions import ObjectDoesNotExist
import time
import datetime
import uuid

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })

class GrabWhatHandler(WeChatHandler):

    def check(self):
        return　self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        currenttime = str(datetime.datetime.now())
        for act in Activity.objects.filter(status=Activity.STATUS_PUBLISHED):
            endtime = str(act.end_time)
            if endtime <= currenttime:
                act.status = Activity.STATUS_SAVED
                act.save()
        activitys = []
        for act in Activity.objects.filter(status=Activity.STATUS_PUBLISHED).order_by)('book_start'):
            activitys.append({
                'Title':act.name,
                'Description':act.description,
                'PicUrl':act.pic_url,
                'Url':settings.get_url('u/activity') + '?id=' + str(act.id)
            })
        return self.reply_news(articles=activitys)
       # activity = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        #return self.reply_text(self.get_message('book_what', activity=activity))


class CheckTicketHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['get_ticket'])
    def handle(self):
        ticket = Ticket.objects.exclude(student_id=self.user.student_id,status=Ticket.STATUS_CANCELLED)
        return self.reply_text(self.get_message('get_ticket', ticket=ticket))




class GrabTicketHandler(WeChatHandler):

    def check(self):
        return self.is_msg_type('event') and (self.input['Event'] == 'CLICK') and self.view.event_keys['book_header'] in self.input['EventKey']
    def handle(self):
        current_student_id = self.user.student_id
        current_open_id = self.user.open_id
        activities = Activity.objects.filter(status=1)
        for act in activities:
            if str(act.id) in self.input['EventKey']:
                finally_activity = act
                break
        mybooked_ticket = Ticket.objects.filter(student_id=current_student_id)
        for tic in mybooked_ticket:
            if tic.activity == finally_activity:
                return self.reply_text(self.get_message('ticket_detail',ticket=tic))
        starttime = str(finally_activity.book_start)
        endtime = str(finally_activity.book_end)
        currenttime = str(datetime.datetime.now())
        if starttime > currenttime:
            return self.reply_text(self.get_message('activity_detail', activity=finally_activity))
        elif endtime < currenttime:
            return self.reply_text("抢票已经结束 T T")
        elif finally_activity.remain_tickets>0:
            try:
                Ticket.objects.create(student_id=current_student_id,
                                     unique_id=uuid.uuid1(),
                                     activity=finally_activity,
                                     status=Ticket.STATUS_VALID,
                                     )
            except TransactionManagementError:
                return self.reply_text("出票失败")
            else:
                finally_activity.remain_tickets = finally_activity.remain_tickets - 1
                finally_activity.save()
                tic = Ticket.objects.get(student_id=current_student_id,activity=finally_activity,status=1)
                return self.reply_text(self.get_message('ticket_grab_success', ticket=tic))

        else:
            return  self.reply_text("抱歉，票已抢空 T T")


class GrabTicketinWritingHandler(WeChatHandler):

    def check(self):
        return self.is_msg_type('text') and '抢票' in self.input['Content']
    def handle(self):
        strings = self.input['Content']
        strings = strings.spilt()[-1]
        current_student_id = self.user.student_id
        try:
            Activity.objects.get(status=1,key=strings)
        except ObjectDoesNotExist:
            return self.reply_text("对不起，您所抢的票不存在，请查看是否输入正确")
        finally_activity = Activity.objects.get(status=1, key=strings)
        mybooked_ticket = Ticket.objects.filter(student_id=current_student_id)
        for tic in mybooked_ticket:
            if tic.activity == finally_activity:
                return self.reply_text("你已经预定过了(> <)")
        starttime = str(finally_activity.book_start)
        endtime = str(finally_activity.book_end)
        currenttime = str(datetime.datetime.now())
        if starttime > currenttime:
            return self.reply_text(self.get_message('activity_detail', activity=finally_activity))
        elif endtime < currenttime:
            return self.reply_text("抢票已经结束 T T")
        elif finally_activity.remain_tickets > 0:
            try:
                Ticket.objects.create(student_id=current_student_id,
                                      unique_id=uuid.uuid1(),
                                      activity=finally_activity,
                                      status=Ticket.STATUS_VALID,
                                      )
            except TransactionManagementError:
                return self.reply_text("出票失败")
            else:
                finally_activity.remain_tickets = finally_activity.remain_tickets - 1
                finally_activity.save()
                tic = Ticket.objects.get(student_id=current_student_id, activity=finally_activity, status=1)
                return self.reply_text(self.get_message('ticket_grab_success', ticket=tic))
        else:
            return self.reply_text("抱歉，票已抢空 T T")


class DeleteTicketHandler(WeChatHandler):

    def check(self):
        return self.is_msg_type('text') and '退票' in self.input['Content']
    def handle(self):
        strings = self.input['Content']
        strings = strings.spilt()[-1]
        tickets = Ticket.objects.filter(student_id=self.user.student_id, status=1)
        flag = 0
        for tic in tickets:
            if tic.activity.key == strings:
                flag = 1
                tic.status = 0
                tic.save()
        if flag == 0:
            return self.reply_text("您所退的票不存在，请查看是否输入正确")
        else:
            activity = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
            return self.reply_text(self.get_message('book_what', activity=activity))
            return self.reply_text("退票成功")


class UnbindOrUnsubscribeHandler(WeChatHandler)

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


