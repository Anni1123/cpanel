from django.shortcuts import render
import pyrebase
from django.contrib import auth
config = {
    "apiKey": "AIzaSyAQNiKbRtnsik24ra5oBjC9RsVKKDok0vY",
    "authDomain": "uploadsusingfirebase.firebaseapp.com",
    "databaseURL": "https://uploadsusingfirebase.firebaseio.com",
    "projectId": "uploadsusingfirebase",
    "storageBucket": "uploadsusingfirebase.appspot.com",
    "messagingSenderId": "2985001082",
    "appId": "1:2985001082:web:d1dc633ca5eb7464a17bc3"
  }

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

def signIn(request):
    return render(request,"sigIn.html")

def postsignIn(request):

    email=request.POST.get('email')
    pasw=request.POST.get('pass')
    try:
        user=authe.sign_in_with_email_and_password(email,pasw)
    except:
        message="Invalid Credentials!!Please Chech your Data"
        return render(request,"sigIn.html",{"message":message})
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    return render(request,"welcome.html",{"email":email})

def logout(request):
    try:
        del request.session['uid']
    except:
        pass
    return render(request,"sigIn.html")

def signUp(request):
    return render(request,"signUp.html")

def postsignUp(request):

     email = request.POST.get('email')
     passs = request.POST.get('pass')
     name = request.POST.get('name')
     try:
        user=authe.create_user_with_email_and_password(email,passs)
        uid = user['localId']
        idtoken = request.session['uid']
        print(uid)
        data = {"name": name, "status": "1"}
        database.child("users").child(uid).child("details").set(data)
     except:
        message = "Wanna View Our Website...Please Sign Up First! "
        return render(request, "signUp.html", {"message": message})
     return render(request,"sigIn.html")

def create(request):
    return render(request,"check.html")

def postcreate(request):
    import time
    from datetime import datetime,timezone
    import pytz

    tz=pytz.timezone('Asia/Kolkata')
    time_now=datetime.now(timezone.utc).astimezone(tz)
    millis=int(time.mktime(time_now.timetuple()))
    work=request.POST.get('work')
    progress=request.POST.get('progress')
    url = request.POST.get('url')
    data = {
        "work": work,
        "progress": progress,
        "url":url
    }
    try:
        idtoken=request.session['uid']
        if idtoken:
            a=authe.get_account_info(idtoken)
            a=a['users']
            a=a[0]
            a=a['localId']
            database.child('users').child(a).child('reports').child(millis).set(data)
            name=database.child('users').child(a).child('details').child('name').get().val()
            push_notify(name,progress,work)
            return render(request,'welcome.html',{"email":name})
    except:
        message = "Oops!!You Logged out..please Sign in Again to visit our website"
        return render(request, "sigIn.html", {"message": message})


def check(request):
    import datetime
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    timestamp=database.child('users').child(a).child('reports').shallow().get().val()

    lis_time=[];
    for i in timestamp:
        lis_time.append(i)
    works=[]
    for i in lis_time:
        work=database.child('users').child(a).child('reports').child(i).child('work').get().val()
        progress=database.child('users').child(a).child('reports').child(i).child('progress').get().val()
        works.append(work)
    date=[]
    for i in timestamp:
        i=float(i)
        dat=datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%y')
        date.append(dat)

    comb_lis=zip(lis_time,date,works)
    name = database.child('users').child(a).child('details').child('name').get().val()
    return render(request, "create.html",{"comb_lis":comb_lis,"e":name})

def post_check(request):
    import datetime
    time=request.GET.get("z")
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    work = database.child('users').child(a).child('reports').child(time).child('work').get().val()
    progress = database.child('users').child(a).child('reports').child(time).child('progress').get().val()
    img = database.child('users').child(a).child('reports').child(time).child('url').get().val()
    time=float(time)
    print(img)
    dat = datetime.datetime.fromtimestamp(time).strftime('%H:%M %d-%m-%y')
    name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request, "post_check.html",{"w":work,"p":progress,'d':dat,"name":name,"url":img})

def push_notify(name,progress,work):
    from pusher_push_notifications import PushNotifications

    beams_client = PushNotifications(
        instance_id='068acacc-d54f-4853-ab93-a2ffbb3b4f89',
        secret_key='2965ADD942C08D08770BD5767E0D2949C0A467B1002DE65179D539F4302759DE',
    )
    response = beams_client.publish_to_interests(
        interests=['hello'],
        publish_body={
            'apns': {
                'aps': {
                    'alert': 'Report created!'
                }
            },
            'fcm': {
                'notification': {
                    'title': str(name),
                    'body': "Progress :" + str(progress) + "work :"+ str(work)
                }
            }
        }
    )

    print(response['publishId'])
