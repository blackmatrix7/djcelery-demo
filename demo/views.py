from django.http import HttpResponse
from demo.tasks import async_demo_task


# Create your views here.
def demo_task(request):
    async_demo_task.delay()
    return HttpResponse('任务已经运行')



