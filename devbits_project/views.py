from django.shortcuts import render,redirect
from app.models import Categories,Course,Level,Video,UserCourse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum

def BASE(request):
    category=Categories.get_all_category(Categories)
    context={
        'category':category,
    }
    return render(request,'base.html',context)

def INDEX(request):
    category=Categories.objects.all().order_by('id')[0:5]
    course=Course.objects.filter(status='PUBLISH').order_by('id')
    context={
        'category':category,
        'course':course,
    }
    return render(request,'Main/index.html',context)

def SINGLE_COURSE(request):
    category=Categories.get_all_category(Categories)
    level=Level.objects.all()
    course=Course.objects.all()
    FreeCourse_count = Course.objects.filter(price=0).count()
    PaidCourse_count= Course.objects.filter(price__gte=1).count()
    context={
        'category':category,
        'level':level,
        'course':course,
        'FreeCourse_count':FreeCourse_count,
        'PaidCourse_count':PaidCourse_count,
    }
    return render(request,'Main/single_course.html',context)

def filter_data(request):
    category = request.GET.getlist('category[]')
    level = request.GET.getlist('level[]')
    price = request.GET.getlist('price[]')
    # print(price)
    if price == ['PriceFree']:
       course = Course.objects.filter(price=0)
    elif price == ['PricePaid']:
       course = Course.objects.filter(price__gte=1)
    elif price == ['PriceAll']:
       course = Course.objects.all()
    if category:
       course = Course.objects.filter(category__id__in=category).order_by('-id')
    elif level:
       course = Course.objects.filter(level__id__in = level).order_by('-id')
    else:
       course = Course.objects.all().order_by('-id')
    category=Categories.get_all_category(Categories)
    context={
        'course':course,
        'category':category,
    }
    t = render_to_string('ajax/course.html',context)

    return JsonResponse({'data': t})

def CONTACT_US(request):
    category=Categories.get_all_category(Categories)
    context={
        'category':category,
    }
    return render(request,'Main/contact_us.html',context)

def ABOUT_US(request):
    category=Categories.get_all_category(Categories)
    context={
        'category':category,
    }
    return render(request,'Main/about_us.html',context)

def SEARCH_COURSE(request):
    query = request.GET['query']
    course = Course.objects.filter(title__icontains = query)
    category=Categories.get_all_category(Categories)
    context={
        'course':course,
        'category':category,
    }
    return render(request,'search/search.html',context)

def COURSE_DETAILS(request,slug):
    course=Course.objects.filter(slug = slug)
    category=Categories.get_all_category(Categories)
    time_duration=Video.objects.filter(course__slug=slug).aggregate(sum=Sum('time_duration'))
    
    course_id=Course.objects.get(slug=slug)
    check_enroll = None
    if request.user.is_authenticated:
        try:
            check_enroll=UserCourse.objects.get(user=request.user,course=course_id)
        except UserCourse.DoesNotExist:
            check_enroll=None
        except UserCourse.MultipleObjectsReturned:
            check_enroll = UserCourse.objects.filter(user=request.user, course=course_id).first()

    if course.exists():
        course=course.first()
    else:
        return redirect('404')
    context={
        'course':course,
        'category':category,
        'time_duration':time_duration,
        'check_enroll':check_enroll,
    }
    return render(request,'course/course_details.html',context)

def PAGE_NOT_FOUND(request):
    category=Categories.get_all_category(Categories)
    context={
        'category':category,
    }
    return render(request,'error/404.html',context)

def CHECKOUT(request,slug):
    course=Course.objects.get(slug=slug)
    category=Categories.get_all_category(Categories)
    if course.price == 0:
        course=UserCourse(
            user = request.user,
            course=course,
        )
        course.save()
        messages.success(request,'Course Are Successfully Enrolled!')
        return redirect('my_course')
    context={
        'course':course,
        'category':category,
    }
    return render(request,'checkout/checkout.html',context)

def MY_COURSE(request):
    course = UserCourse.objects.filter(user = request.user)
    category=Categories.get_all_category(Categories)
    context={
        'course':course,
        'category':category,
    }
    return render(request,'course/my-course.html',context)

def WATCH_COURSE(request,slug):
    category=Categories.get_all_category(Categories)
    context={
        'category':category,
    }
    return render(request,'course/watch-course.html',context)

def handlelogout(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('index')

