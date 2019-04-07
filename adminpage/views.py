from django.shortcuts import render
#xinzengtian
#from wechat.views import CustomWeChatView.update_menu

from django.contrib.auth import authenticate, login,logout
from django.db.transaction import TransactionManagementError
from django.core.exceptions import ObjectDoesNotExist
from wechat.views import CustomWeChatView
from wechat.models import *
from codex.baseerror import *
from codex.baseview import APIView
from WeChatTicket.settings import MEDIA_ROOT,MEDIA_URL
import datetime
import time


# Create your views here.


class LoginView(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValueError("用户错误")
    def post(self):
        user = authenticate(username=self.input['username'], pa ssword=self.input['password'])
        if user is not None:
           if user.is_active:
               login(self.request, user)


class LogoutView(APIView):

    def post(self):
        if self.request.user.is_authenticated():
            logout(self.request)
        else 
            raise ValueError("已经退出登录")


class ActivityList(APIView):

    def get(self):
        array = []
        for activity in Activity.objects.filter(status__gte=0):
            obj = {
                'id':activity.id,
                'name':activity.name,
                'description':activity.description,
                'startTime':time.mktime(activity.start_time.timetuple()),
                'endTime':time.mktime(activity.end_time.timetuple()),
                'place':activity.place,
                'bookStart':time.mktime(activity.book_start.timetuple()),
                'bookEnd':time.mktime(activity.book_end.timetuple()),
                'currentTime':time.mktime(datetime.datetime.now().timetuple()),
                'status':activity.status
            }
            array.append(obj)
        return array

class ActivityDelete(APIView):

    def post(self):
        self.check_input('id');
        try:
            Activity.objects.filter(id=self.input['id']).delete()
        except TransactionManagementError:
            raise LogicError("delete fail")

class ActivityCreate(APIView):

    def post(self):
        self.check_input('name','key','place','description','picUrl','startTime','endTime','bookStart','bookEnd','totalTickets','status')
        try:
            Activity.objects.create(name = self.input['name'],
                                    key = self.input['key'],
                                    place = self.input['place'],
                                    description = self.input['description'],
                                    pic_url = self.input['picUrl'],
                                    start_time = self.input['startTime'],
                                    end_time = self.input['endTime'],
                                    book_start = self.input['bookStart'],
                                    book_end = self.input['bookEnd'],
                                    remain_tickets = self.input['totalTickets'],
                                    total_tickets = self.input['totalTickets'],
                                    status = self.input['status'])
        except TransactionManagementError:
            raise LogicError("create fail")

class ImageUpload(APIView):

    def post(self):
        self.check_input('image')
        picture = self.input['image']
        picture_name = picture.name
        picture_path = MEDIA_URL + '/'+picture_name
        openfile = open(picture_path,'w+b')
        openfile.write(picture.read())
        openfile.close()
        return 'http://139.199.98.175/media/'+picture_name


class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except ObjectDoesNotExist:
            raise LogicError("The Activity is not exist")
        else:
            array = {'name':activity.name,
                     'key':activity.key,
                     'description':activity.description,
                     'startTime':time.mktime(activity.start_time.timetuple()),
                     'endTime':time.mktime(activity.end_time.timetuple()),
                     'place':activity.place,
                     'bookStart':time.mktime(activity.book_start.timetuple()),
                     'bookEnd':time.mktime(activity.book_end.timetuple()),
                     'totalTicket':activity.total_tickets,
                     'picUrl':activity.pic_url,
                     'bookedTickets':activity.total_tickets,
                     'usedTickets': activity.total_tickets,
                     'currentTime':time.mktime(datetime.datetime.now().timetuple()),
                     'status':activity.status}
            return array

    def post(self):
        self.check_input('id','name','key','place','description','picUrl','startTime','endTime','bookStart','bookEnd','totalTickets','status')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except ObjectDoesNotExist:
            raise LogicError("Wrong Activity")
        else:
            activity.name = self.input['name']
            activity.key = self.input['key']
            activity.place = self.input['place']
            activity.description = self.input['description']
            activity.pic_url = self.input['picUrl']
            activity.start_time = self.input['startTime']
            activity.end_time = self.input['endTime']
            activity.book_start = self.input['bookStart']
            activity.book_end = self.input['bookEnd']
            activity.total_tickets =self.input['totalTicket']
            activity.status = self.input['status']
            activity.save()

class ActivityMenu(APIView):
    def get(self):
        if not self.request.user:
            raise ValidateError("you are logout")
        array = []
        current_menu = CustomWeChatView.lib.get_wechat_menu()
        existed_buttons = list()
        for btn in current_menu:
            if btn['name'] == '抢票':
                existed_buttons += btn.get('sub_button', list())
        activities = Activity.objects.filter(status__gte=0)
        for act in activities:
            flag = 0
            finallyflag = 0
            for btn in existed_buttons:
                flag = flag + 1
                if str(act.id) in btn['key']:
                    finallyflag = flag
            obj = {
                'id':activity.id,
                'name':activity.name,
                'menuIndex':finallyflag,
            }
            array.append(obj)
        return array
        #current_menu = CustomWeChatView.lib.get_wechat_menu()
        #existed_buttons = list()
        #for btn in current_menu:
        #    if btn['name'] == '抢票':
        #        existed_buttons += btn.get('sub_button', list())
        #flag = 1
        #array = []
        #for btn in existed_buttons:
        #    for activity in Activity.objects.filter(status__gte=0):
        #        if str(activity.id) in btn['key']:
        #            obj = {
        #                'id':activity.id,
        #                'name':activity.name,
        #                'menuIndex':flag,
        #            }
        #            array.append(obj)
        #            flag = flag + 1
        #           break
        #raise LogicError("array kcd )
        #return array
    def post(self):
        if not self.request.user:
            raise ValidateError("you are logout")
        ides = self.input
        array = []
        for each_id in ides:
            act = Activity.objects.get(id=each_id)
            array.append(act)
        CustomWeChatView.update_menu(array)


class ActivityCheckin(APIView):

    def post(self):
        if not self.request.user:
            raise ValidateError("you are logout")
        self.check_input('actId')
        dic = self.input.keys()
        flag = 0
        for value in dic:
            if value == 'student_id':
                flag = 1
            else if value == 'ticket':
                flag = 2

        if flag == 1:
            tickets = Ticket.objects.filter(student_id=self.input['student_id'])
            for tic in tickets:
                if str(tic.activity.id) == self.input['actId']:
                    tic.status = Ticket.STATUS_USED
                    tic.save()
                    return {
                        'ticket':tic.unique_id
                        'studentId':self.input['studentId']
                    }
            raise LogicError("未检到相应的票")
        elif flag == 2:
            try:
                tickets = Ticket.objects.get(unique_id=self.input['ticket'])
            except ObjectDoesNotExist:
                raise LogicError("未检到相应的票")
            else:
                tic = Ticket.objects.get(unique_id=self.input['ticket'])
                tic.status=Ticket.STATUS_USED
                tic.save()
                return {
                    'ticket': self.input['ticket'],
                    'studentId': tickets.student_id
                }
        else:
            raise LogicError("语法错误")
