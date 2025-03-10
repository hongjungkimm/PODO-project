from django.shortcuts import get_object_or_404, render, redirect
from django.utils.safestring import mark_safe
from workspaces.models import Workspace, Category
from .models import Schedule
from .forms import ScheduleForm
from .calendar import Calendar
import datetime
import calendar
from django.http import JsonResponse
from workspaces.forms import WorkspaceForm, CategoryForm
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from django.contrib.auth.decorators import login_required


@login_required
@require_safe
def index(request, workspace_pk):
    today = get_date(request.GET.get('month'))
    calendar = Calendar(today.year, today.month)
    # calendar.setfirstweekday(calendar.SUNDAY)
    html_calendar = calendar.formatmonth(workspace_pk, withyear=True)
    schedule_form = ScheduleForm()
    workspace_list = Workspace.objects.order_by('-pk')
    workspaces = []
    user = request.user
    for work in workspace_list:
        if user.groups.filter(name= work.id):
            workspaces.append(work)
    workspace_form = WorkspaceForm()
    workspace_indivisual = get_object_or_404(Workspace, pk=workspace_pk)
    category_form = CategoryForm()
    categories = Category.objects.all()

    context = {
      'calendar': mark_safe(html_calendar),
      'workspace_pk': workspace_pk,
      'workspace_name': workspace_indivisual.name,
      'year': today.year,
      'month': today.month,
      'schedule_form': schedule_form,
      'workspace_form': workspace_form,
      'workspaces': workspaces,
      'category_form' : category_form ,
      'workspace_indivisual' : workspace_indivisual,
      'categories': categories,
    }
    return render(request, 'schedules/index.html', context)


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.datetime.today()


def left_month(request, workspace_pk):
    today = get_date(request.GET.get('month'))
    left_year, left_month = prev_month(today)
    calendar = Calendar(int(left_year), int(left_month))
    # calendar.setfirstweekday(calendar.SUNDAY)
    html_calendar = calendar.formatmonth(workspace_pk, withyear=True)

    context = {
      'calendar': mark_safe(html_calendar),
      'workspace_pk': workspace_pk,
      'left_year': left_year,
      'left_month': left_month,
    }
    return JsonResponse(context)


def right_month(request, workspace_pk):
    today = get_date(request.GET.get('month'))

    right_year, right_month = next_month(today)

    calendar = Calendar(int(right_year), int(right_month))
    # calendar.setfirstweekday(calendar.SUNDAY)
    html_calendar = calendar.formatmonth(workspace_pk, withyear=True)

    context = {
      'calendar': mark_safe(html_calendar),
      'workspace_pk': workspace_pk,
      'right_year': right_year,
      'right_month': right_month,
    }
    return JsonResponse(context)


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.datetime.today()


def prev_month(day):
    first = day.replace(day=1)
    prev_month = first - datetime.timedelta(days=1)
    year = str(prev_month.year)
    month = str(prev_month.month)
    return year, month


def next_month(day):
    days_in_month = calendar.monthrange(day.year, day.month)[1]
    last = day.replace(day=days_in_month)
    next_month = last + datetime.timedelta(days=1)
    year = str(next_month.year)
    month = str(next_month.month)
    return year, month


@login_required
@require_http_methods(['GET', 'POST'])
def create_schedule(request, workspace_pk):
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    if request.method == 'POST':
      form = ScheduleForm(request.POST)
      if form.is_valid():
        schedule = form.save(commit=False)
        schedule.author = request.user
        schedule.workspace = workspace
        schedule.save()
    return redirect('schedules:index', workspace_pk)
    

@login_required
@require_http_methods(['GET', 'POST'])
def update_schedule(request, workspace_pk, schedule_pk):
    schedule = get_object_or_404(Schedule, pk=schedule_pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
        return redirect('schedules:index', workspace_pk)
    else:
        schedule_title = schedule.title
        schedule_content = schedule.content
        schedule_priority = schedule.priority
        schedule_start_date = schedule.start_date.strftime('%Y-%m-%d')
        schedule_end_date = schedule.end_date.strftime('%Y-%m-%d')
        schedule_start_time = schedule.start_time.strftime('%H:%M:%S')
        schedule_end_time = schedule.end_time.strftime('%H:%M:%S')
        context = {
            'schedule_title': schedule_title,
            'schedule_content': schedule_content,
            'schedule_priority': schedule_priority,
            'schedule_start_date': schedule_start_date,
            'schedule_end_date': schedule_end_date,
            'schedule_start_time': schedule_start_time,
            'schedule_end_time': schedule_end_time,
        }
        return JsonResponse(context)


@require_POST
def delete_schedule(request, workspace_pk, schedule_pk):
    schedule = get_object_or_404(Schedule, pk=schedule_pk)
    if request.user.is_authenticated:
        schedule.delete()
        print('삭제완료')
        return redirect('schedules:index', workspace_pk)
    return redirect('schedules:index', workspace_pk)