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
        message="Invalid Credentials"
        return render(request,"sigIn.html",{"message":message})
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    return render(request,"welcome.html",{"email":email})

def logout(request):
    auth.logout(request)
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
        print(uid)
        data = {"name": name, "status": "1"}
        database.child("users").child(uid).child("details").set(data)
     except:
        message = "Invalid Credentials"
        return render(request, "signUp.html", {"message": message})
     return render(request,"sigIn.html")
