from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django_otp.plugins.otp_totp.models import TOTPDevice
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
            return redirect('home')
    return render(request, 'add_poll.html')

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'poll.html', {'poll': poll})

def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    option_id = request.POST.get('option')
    if option_id:
        option = get_object_or_404(Option, id=option_id, poll=poll)
        option.votes += 1
        option.save()
        return redirect('poll_result', poll_id=poll.id)
    return redirect('poll_detail', poll_id=poll.id)

def poll_result(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'poll_result.html', {'poll': poll})
def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        otp_token = request.POST.get("otp_token")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check OTP
            totp_device = TOTPDevice.objects.filter(user=user).first()
            if totp_device and totp_device.verify_token(otp_token):
                login(request, user)
                
                # Redirect based on user type
                if user.is_staff:  # Admin users
                    return redirect(reverse('homeadmin'))  # Redirect to admin homepage
                else:  # Normal users
                    return redirect(reverse('questions'))  # Redirect to questions page
            else:
                return render(request, "login.html", {"error": "Invalid OTP"})
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})
    
    return render(request, "login.html")
def questions_view(request):
    print("Rendering Questions.html")
    return render(request, 'Questions.html')
  # Case-sensitive


def homeadmin(request):
    return render(request, 'homepage.html')  # Ensure homepage.html exists


def add_poll(request):
    if request.method == "POST":
        question = request.POST.get('question')
        options = request.POST.getlist('option[]')
        if question and options:
            poll = Poll.objects.create(question=question)
            for option in options:
                Option.objects.create(poll=poll, text=option)
            return redirect('homeadmin')  # Redirect back to admin homepage after creating poll
    return render(request, 'add_poll.html')




def poll_result(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    total_votes = sum(option.votes for option in poll.options.all())  # Use poll.options instead of poll.option_set

    # Calculate percentage for each option
    for option in poll.options.all():  # Use poll.options here too
        option.percentage = (option.votes / total_votes * 100) if total_votes > 0 else 0

    return render(request, 'poll_result.html', {'poll': poll})


def add_poll(request):
    if request.method == "POST":
        question = request.POST.get('question')  # Get the poll question
        options = request.POST.getlist('option[]')  # Get the list of options
        
        if question and options:  # Ensure both question and options are provided
            # Save the poll question
            poll = Poll.objects.create(question=question)

            # Save each option
            for option_text in options:
                Option.objects.create(poll=poll, text=option_text)

            # Redirect to the admin home page after saving
            return redirect('homeadmin')

    return render(request, 'add_poll.html')

from django.shortcuts import render
from .models import Poll

def view_polls(request):
    polls = Poll.objects.prefetch_related('options').all()  # Fetch all polls with options
    return render(request, 'view_polls.html', {'polls': polls})

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'poll.html', {'poll': poll})




def questions_view(request):
    # Filter only active polls for regular users
    polls = Poll.objects.filter(is_active=True)

    # Annotate polls with whether the current user has voted
    user_votes = UserVote.objects.filter(user=request.user)
    voted_polls = {vote.poll_id for vote in user_votes}

    polls_with_vote_status = []
    for poll in polls:
        polls_with_vote_status.append({
            'poll': poll,
            'has_voted': poll.id in voted_polls
        })

    return render(request, 'Questions.html', {'polls_with_vote_status': polls_with_vote_status})




def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    # Check if the user has already voted
    if UserVote.objects.filter(user=request.user, poll=poll).exists():
        # User has already voted; just render the page with options frozen
        return render(request, 'poll.html', {'poll': poll, 'voted': True})

    if request.method == "POST":
        option_id = request.POST.get("option")
        if option_id:
            option = get_object_or_404(Option, id=option_id, poll=poll)
            option.votes += 1
            option.save()

            # Record the user's vote
            UserVote.objects.create(user=request.user, poll=poll)

            # Render the page with options frozen
            return render(request, 'poll.html', {'poll': poll, 'voted': True})

    return render(request, 'poll.html', {'poll': poll})

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Allow AJAX requests without CSRF token for testing (not recommended for production)
def toggle_poll_status(request, poll_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON payload
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

# Delete a poll
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
        # Fetch all polls and their options
        polls = Poll.objects.prefetch_related('options').all()

        # Debug log: Check if polls are being fetched
        print("Fetched polls:", polls)

        # Calculate vote percentages for each option
        for poll in polls:
            total_votes = sum(option.votes for option in poll.options.all())
            for option in poll.options.all():
                option.percentage = (option.votes / total_votes * 100) if total_votes > 0 else 0

                # Debug log for each option
                print(f"Poll: {poll.question}, Option: {option.text}, Votes: {option.votes}, Percentage: {option.percentage}")

        return render(request, 'poll_result.html', {'polls': polls})

    except Exception as e:
        print("Error occurred:", e)
        return render(request, 'poll_result.html', {'polls': []})





from django.shortcuts import render
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
import pyotp
import qrcode
import io
import base64


def add_user_and_qr(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "add_user_and_qr.html", {"error": "Username already exists."})

        # Step 1: Create the user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Step 2: Generate a valid Base32 TOTP secret
        base32_secret = pyotp.random_base32()

        # Step 3: Convert Base32 to binary
        binary_key = pyotp.TOTP(base32_secret).byte_secret()


        # Step 4: Create the TOTP Device and save binary key
        totp_device = TOTPDevice.objects.create(user=user, confirmed=True, name="Default TOTP")
        totp_device.key = binary_key.hex()  # Save as hex string
        totp_device.save()

        # Step 5: Generate the provisioning URI
        totp = pyotp.TOTP(base32_secret)
        provisioning_uri = totp.provisioning_uri(name=username, issuer_name="Pollister App")

        # Step 6: Generate QR Code
        qr = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Render the template with the QR Code
        return render(request, "add_user_and_qr.html", {"qr_code": qr_base64, "username": username})

    return render(request, "add_user_and_qr.html", {})










