from codex.baseerror import *
from codex.baseview import APIView
from django.core.exceptions import ObjectDoesNotExist
from wechat.models import *
import datetime
import time

class UserBind(APIView):

    def validate_user(self):

        
        """
        input: self.input[' '] and self.input['password']
        raise: ValidateError when validating failed
        """
        raise NotImplementedError('You should implement UserBind.validate_user method')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id 

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityDetail(APIView):

    def get(self):
        self.check_input('id');
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except ObjectDoesNotExist:
            raise LogicError("The Activity is not exist")
        else:
            array = {'name': activity.name,
                     'key': activity.key,
                     'description': activity.description,
                     'startTime': time.mktime(activity.start_time.timetuple()),
                     'endTime': time.mktime(activity.end_time.timetuple()),
                     'place': activity.place,
                     'bookStart': time.mktime(activity.book_start.timetuple()),
                     'bookEnd': time.mktime(activity.book_end.timetuple()),
                     'totalTicket': activity.total_tickets,
                     'picUrl': activity.pic_url,
                     'remainTickets':activity.remain_tickets,
                     'currentTime': time.mktime(datetime.datetime.now().timetuple())}
            return array


class TicketDetail(APIView):

    def get(self):
        self.check_input('openid','ticket')
        try:
            myticket = Ticket.objects.get(unique_id=self.input['ticket'])
        except ObjectDoesNotExist:
            raise LogicError("The Ticket is not exist")
        else:
            array = {'activityName': myticket.activity.name,
                     'place': myticket.activity.place,
                     'activityKey': myticket.activity.key,
                     'uniqueId':myticket.unique_id
                     'startTime': time.mktime(myticket.activity.start_time.timetuple()),
                     'endTime': time.mktime(myticket.activity.end_time.timetuple()),
                     'currentTime': time.mktime(datetime.datetime.now().timetuple()),
                     'status': myticket.status}
            return array

