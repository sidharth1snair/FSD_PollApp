from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import logging
from django.http import JsonResponse
from django.urls import reverse
from .models import Poll, Option, UserVote


logger = logging.getLogger(__name__)
from .models import Poll, Option

def home(request):
    polls = Poll.objects.all()
    return render(request, 'login.html', {'polls': polls})

def add_poll(request):
    if request.method == "POST":
        question = request.POST.get('question')
        options = request.POST.getlist('option[]')
        if question and options:
            poll = Poll.objects.create(question=question)
            for option in options:
                Option.objects.create(poll=poll, text=option)
            return redirect('homeadmin')
    return render(request, 'add_poll.html')



def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    option_id = request.POST.get('option')
    if option_id:
        option = get_object_or_404(Option, id=option_id, poll=poll)
        option.votes += 1
        option.save()
        return redirect('poll_result', poll_id=poll.id)
    return redirect('poll_detail', poll_id=poll.id)


def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        otp_token = request.POST.get("otp_token")
        
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            
            totp_device = TOTPDevice.objects.filter(user=user).first()
            if totp_device and totp_device.verify_token(otp_token):
                login(request, user)
                
               
                if user.is_staff:  
                    return redirect(reverse('homeadmin'))  
                else:  
                    return redirect(reverse('questions'))  
            else:
                return render(request, "login.html", {"error": "Invalid OTP"})
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    
    return render(request, "login.html")



def homeadmin(request):
    return render(request, 'homepage.html')  


from django.shortcuts import render
from .models import Poll

def view_polls(request):
    polls = Poll.objects.prefetch_related('options').all()  
    return render(request, 'view_polls.html', {'polls': polls})


def questions_view(request):
    
    polls = Poll.objects.filter(is_active=True)

   
    user_votes = UserVote.objects.filter(user=request.user)
    voted_polls = {vote.poll_id for vote in user_votes}

    polls_with_vote_status = []
    for poll in polls:
        polls_with_vote_status.append({
            'poll': poll,
            'has_voted': poll.id in voted_polls
        })

    return render(request, 'Questions.html', {'polls_with_vote_status': polls_with_vote_status})




from django.http import JsonResponse

def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    
    if UserVote.objects.filter(user=request.user, poll=poll).exists():
        return JsonResponse({'success': False, 'error': 'You have already voted'}, status=400)

    if request.method == "POST":
        option_id = request.POST.get("option")
        if option_id:
            option = get_object_or_404(Option, id=option_id, poll=poll)
            option.votes += 1
            option.save()

           
            UserVote.objects.create(user=request.user, poll=poll)

            
            return JsonResponse({'success': True, 'message': 'Vote submitted successfully'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


from django.views.decorators.csrf import csrf_exempt
import json


def toggle_poll_status(request, poll_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            is_active = data.get('is_active', None)

            if is_active is None:
                return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

            poll = get_object_or_404(Poll, id=poll_id)
            poll.is_active = is_active
            poll.save()

            return JsonResponse({'success': True, 'is_active': poll.is_active})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def delete_poll(request, poll_id):
    if request.method == 'DELETE':
        poll = get_object_or_404(Poll, id=poll_id)
        poll.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)



from django.shortcuts import render, get_object_or_404
from .models import Poll

def poll_result(request):
    try:
       
        polls = Poll.objects.prefetch_related('options').all()

        for poll in polls:
            total_votes = sum(option.votes for option in poll.options.all())
            for option in poll.options.all():
                option.percentage = (option.votes / total_votes * 100) if total_votes > 0 else 0

        return render(request, 'poll_result.html', {'polls': polls})

    except Exception as e:
        print("Error occurred:", e)
        return render(request, 'poll_result.html', {'polls': []})


from django.shortcuts import render
from django.contrib.auth.models import User
import pyotp
import qrcode
import io
import base64


def add_user_and_qr(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        
        if User.objects.filter(username=username).exists():
            return render(request, "add_user_and_qr.html", {"error": "Username already exists."})

       
        user = User.objects.create_user(username=username, email=email, password=password)

        base32_secret = pyotp.random_base32()
       
        binary_key = pyotp.TOTP(base32_secret).byte_secret()
        
        totp_device = TOTPDevice.objects.create(user=user, confirmed=True, name="Default TOTP")
        totp_device.key = binary_key.hex()  
        totp_device.save()

        
        totp = pyotp.TOTP(base32_secret)
        provisioning_uri = totp.provisioning_uri(name=username, issuer_name="Pollister App")

       
        qr = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

       
        return render(request, "add_user_and_qr.html", {"qr_code": qr_base64, "username": username})

    return render(request, "add_user_and_qr.html", {})










