from datetime import date
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from .models import Event, RSVP
from .forms import (
    SignUpForm,
    EventForm,
    
    RSVPForm,
    UpdateUserForm,
    OptionalPasswordChangeForm
)
from .mailgun_email import send_mailgun_email



# ------------------- HOME -------------------


@login_required
def home(request):
    now = timezone.now().date()

    # ✅ Only include non-deleted events
    events = Event.objects.filter(owner=request.user, is_deleted=False)

    upcoming = events.filter(date__gt=now)
    running = events.filter(date=now)
    past = events.filter(date__lt=now)

    stats = {
        'total': events.count(),
        'upcoming': upcoming.count(),
        'running': running.count(),
        'past': past.count()
    }

    return render(request, 'planner/home.html', {
        'events': events,
        'upcoming': upcoming,
        'stats': stats
    })



# ------------------- SIGNUP -------------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'planner/signup.html', {'form': form})


# ------------------- LOGIN -------------------

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pwd = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=pwd)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'planner/login.html', {'error': 'Invalid email or password'})
    return render(request, 'planner/login.html')



# ------------------- LOGOUT -------------------
def logout_view(request):
    logout(request)
    return redirect('home')




# ------------------- CREATE EVENT -------------------


@login_required(login_url='login')
def create_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user

            # Generate unique video link
            room_code = get_random_string(8)
            event.video_link = f"https://meet.jit.si/Gatherly_{room_code}"
            event.save()

            # Send emails
            to_emails = form.cleaned_data.get('guest_emails')
            subject = f"You're invited to: {event.title}"
            for email in to_emails.split(","):
                email = email.strip()
                if email:
                    rsvp_url = request.build_absolute_uri(
                        reverse('rsvp', args=[event.id])
                    ) + f"?guest={email}"
                    message = f"""Hello,

You are invited to an event via Gatherly.

Title: {event.title}
Date: {event.date}
Time: {event.time}
Location: {event.location}

Join Video Call: {event.video_link}
RSVP Here: {rsvp_url}

Best regards,
Gatherly Team
"""
                    send_mailgun_email(email, subject, message)

            # ✅ Show toast + clear form
            messages.success(request, "Event created successfully.")
            form = EventForm()  # Clear the form
    else:
        form = EventForm()

    return render(request, 'planner/create_event.html', {'form': form})



# ------------------- MY EVENTS -------------------
@login_required(login_url='login')
def my_events_view(request):
    today = date.today()

    upcoming_events = Event.objects.filter(
        owner=request.user,
        date__gte=today,
        is_deleted=False  # ✅ Only non-deleted
    ).order_by('date').prefetch_related('rsvps')

    past_events = Event.objects.filter(
        owner=request.user,
        date__lt=today,
        is_deleted=False  # ✅ Only non-deleted
    ).order_by('-date').prefetch_related('rsvps')

    return render(request, 'planner/my_events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })


# ------------------- PROFILE -------------------
@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        uform = UpdateUserForm(request.POST, instance=request.user)
        pform = OptionalPasswordChangeForm(request.user, request.POST)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            if pform.cleaned_data:
                pform.save()
                update_session_auth_hash(request, request.user)
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        uform = UpdateUserForm(instance=request.user)
        pform = OptionalPasswordChangeForm(request.user)



    return render(request, 'planner/profile.html', {'uform': uform, 'pform': pform})





# ------------------- CALENDAR -------------------


@login_required(login_url='login')
def calendar_view(request):
    if request.GET.get('format') == 'json':
        today = date.today()

        # ✅ Fetch only non-deleted events for the user
        events = Event.objects.filter(owner=request.user, is_deleted=False)

        data = []
        for e in events:
            try:
                date_part = e.date.isoformat()
                time_part = e.time.strftime('%H:%M:%S') if e.time else "00:00:00"
                full_datetime = f"{date_part}T{time_part}"

                # ✅ Decide dot color class
                if e.date < today:
                    color_class = "dot-gray"
                elif e.date == today:
                    color_class = "dot-blue"
                else:
                    color_class = "dot-green"

                data.append({
                    'id': e.id,
                    'title': e.title,
                    'start': full_datetime,
                    'url': reverse('my_events') + f"#event-{e.id}",
                    'colorClass': color_class  # ✅ Used in eventContent
                })

            except Exception as ex:
                print(f"⚠️ Error processing event {e.id}: {ex}")

        return JsonResponse(data, safe=False)

    # For normal HTML page request
    return render(request, 'planner/calendar.html')



# ------------------- RSVP -------------------  



def rsvp_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    guest_email = request.GET.get('guest')

    # ✅ If the logged-in user is the event owner, show RSVP summary
    if request.user.is_authenticated and request.user == event.owner:
        guest_rsvps = event.rsvps.all()
        return render(request, 'planner/rsvp_summary.html', {
            'event': event,
            'guest_rsvps': guest_rsvps,
        })

    # ✅ If guest accessed via email link or is logged in
    if request.user.is_authenticated:
        rsvp_user = request.user
    elif guest_email:
        rsvp_user, _ = User.objects.get_or_create(
            username=guest_email,
            defaults={"email": guest_email}
        )
    else:
        return HttpResponse("Invalid RSVP link", status=400)

    # ✅ Get or create RSVP instance for this user and event
    rsvp, _ = RSVP.objects.get_or_create(user=rsvp_user, event=event)

    # ✅ If it's a POST request, save form data
    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=rsvp)
        if form.is_valid():
            form.save()
            return render(request, 'planner/rsvp_thanks.html', {'event': event})
    else:
        form = RSVPForm(instance=rsvp)

    # ✅ Show RSVP form for guest
    return render(request, 'planner/rsvp_form.html', {
        'form': form,
        'event': event
    })





# ------------------- EDIT EVENT -------------------


@login_required
def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id, owner=request.user)
    success = False
    no_change = False  # flag to show "no change" message

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            if form.has_changed():  # ✅ check if any field changed
                updated_event = form.save(commit=False)

                if not updated_event.video_link or updated_event.video_link.strip() == "":
                    room_code = get_random_string(8)
                    updated_event.video_link = f"https://meet.jit.si/Gatherly_{room_code}"

                updated_event.save()
                success = True

                subject = f"🔁 Updated: Event '{updated_event.title}'"

                for email in updated_event.guest_emails.split(","):
                    email = email.strip()
                    if email:
                        rsvp_url = request.build_absolute_uri(
                            reverse('rsvp', args=[updated_event.id])
                        ) + f"?guest={email}"

                        message = f"""Hi there,

The event you were invited to has been updated:

 Title: {updated_event.title}
 Date: {updated_event.date}
 Time: {updated_event.time}
 Location: {updated_event.location}

 Join Video Call: {updated_event.video_link}
 RSVP Here: {rsvp_url}

- Gatherly Team
"""

                        response = send_mailgun_email(email, subject, message)
                        if response.status_code == 200:
                            print(f"✅ Update email sent to {email}")
                        else:
                            print(f"❌ Failed to send update email to {email}: {response.text}")
                return redirect('my_events')
            else:
                no_change = True
    else:
        form = EventForm(instance=event)

    return render(request, 'planner/edit_event.html', {
        'form': form,
        'event': event,
        'success': success,
        'no_change': no_change,
    })





# ------------------- DELETE EVENT -------------------
@login_required
def delete_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id, owner=request.user)

    if request.method == 'POST':
        # ✅ Soft delete
        event.is_deleted = True
        event.save()

        # ✅ Send cancellation email
        subject = f"❌ Cancelled: Event '{event.title}'"
        message = f"""Hello,

We're sorry to inform you that the following event has been cancelled:

 Title: {event.title}
 Date: {event.date}
 Time: {event.time}
 Location: {event.location}

Please disregard any previous reminders.

- Gatherly Team
"""

        for email in event.guest_emails.split(","):
            email = email.strip()
            if email:
                response = send_mailgun_email(email, subject, message)
                if response.status_code == 200:
                    print(f"✅ Cancellation email sent to {email}")
                else:
                    print(f"❌ Failed to send cancellation email to {email}: {response.text}")

        return redirect('my_events')

    return render(request, 'planner/confirm_delete.html', {'event': event})




@login_required
def join_video_call(request, event_id):
    event = Event.objects.get(id=event_id, user=request.user)
    return render(request, 'video_call.html', {'video_link': event.video_link})
