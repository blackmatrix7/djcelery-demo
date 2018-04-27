import json
import uuid
import decimal
import datetime
from django.http import HttpResponse
from demo.tasks import async_demo_task
from djcelery.models import PeriodicTask
from django.utils.timezone import is_aware
from django.utils.functional import Promise
from django.utils.duration import duration_iso_string
from django.core.serializers.json import DjangoJSONEncoder

from django.forms.models import model_to_dict


class CustomJSONEncoder(DjangoJSONEncoder):

    datetime_format = '%Y-%m-%d %H:%M:%S'
    date_format = '%Y-%m-%d'

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.strftime(CustomJSONEncoder.datetime_format)
            return r
        elif isinstance(o, datetime.date):
            r = o.strftime(CustomJSONEncoder.date_format)
            return r
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o)
        else:
            return super().default(o)


# Create your views here.
def demo_task(request):
    async_demo_task.delay()
    return HttpResponse('任务已经运行')


def get_periodic_task_list(request):
    """
    获取周期性任务列表
    :return:
    """
    periodic_task_list = PeriodicTask.objects.all()
    data = [model_to_dict(periodic_task) for periodic_task in periodic_task_list]
    resp = json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)
    return HttpResponse(resp, content_type='application/json', status=200)


