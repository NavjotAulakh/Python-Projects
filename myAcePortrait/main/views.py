from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail

from main.models import *
from main.forms import *

#Call to included Django user verification control method
def is_classified(request):
	if not UserProfile.objects.get(user=request.user):
		return redirect('choose_type')

#Defined hunter vs prospect control function defined to guarantee prospects cannot see what hunters should see	
def is_hunter(request):
	profile = UserProfile.objects.get(user=request.user)
	user_type = profile.user_type
	if user_type == 'HUNTER':
		return True
	else:
		return False

#Call to generate typical landing page
def landing(request):
	if request.user.is_authenticated:
		try:
			UserProfile.objects.get(user=request.user)
		except UserProfile.DoesNotExist:
			return redirect ('choose_type')
		if is_hunter(request):
			return redirect('hunter_home')
		else:
			return redirect('prospect_home')
	else:
		return render(request, 'main/landing.html')

#Call to verify that user type allow for appropriate redirect
def choose_type(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = UserProfileForm(request.POST)
			if form.is_valid():
				form = form.save(commit=False)
				form.user = request.user
				form.save()
				return redirect('landing')
		else:
			form = UserProfileForm()
		context = {
			'form': form
		}
		return render(request, 'registration/choose_type.html', context)
	return redirect('landing')

#Call to render appropriate signup response
def signup(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/accounts/login')
	else:
		form = RegistrationForm()
	context = {
		'form': form
	}
	return render(request, 'registration/signup.html', context)


# Hunter Views
def hunter_home(request):
	search_term=''
	if request.user.is_authenticated:
		is_classified(request)
		if is_hunter(request):
			prospects = UserProfile.objects.filter(user_type="PROSPECT")
			prospect_profiles = ProspectProfile.objects.all()
			if 'search' in request.GET:
				search_term = request.GET['search']
				if search_term != '':
					prospect_profiles = ProspectProfile.objects.filter(Q(prospect__username__icontains=search_term) 
						| Q(bio__icontains=search_term) | Q(skills__icontains=search_term))
			else:
				prospect_profiles = ProspectProfile.objects.all()

			context = {
				'prospects': prospects,
				'prospect_profiles': prospect_profiles,
				'search_term': search_term
			}
		return render(request, 'main/hunter/home.html', context)
	return redirect('landing')

#Addition of hunter like functionality
def hunter_like(request, prospect):
	search_term=''
	if request.user.is_authenticated:
		is_classified(request)
		if is_hunter(request):
			if request.method == 'POST':
				hunter = request.user.id
				prospectuser = User.objects.get(pk=prospect)
				prospect = ProspectProfile.objects.get(prospect=prospectuser)

				if prospect.likes.filter(pk=hunter).exists() == False:
					prospect.likes.add(hunter)
					prospect.save()
			prospects = UserProfile.objects.filter(user_type="PROSPECT")

			context = {
				'prospects': prospects
			}
			return redirect('hunter_home')
		return render(request, 'main/hunter/home.html', context)
	return redirect('hunter_home')

#Removal of a provided like by hunter to prospect
def hunter_dislike(request, prospect):
	if request.user.is_authenticated:
		is_classified(request)
		if is_hunter(request):
			if request.method == 'POST':
				hunter = request.user.id
				prospectuser = User.objects.get(pk=prospect)
				prospect = ProspectProfile.objects.get(prospect=prospectuser)

				if prospect.likes.filter(pk=hunter).exists():
					prospect.likes.remove(hunter)
					prospect.save()
		
			prospects = UserProfile.objects.filter(user_type="PROSPECT")
			context = {
				'prospects': prospects
			}
			return redirect('hunter_home')
		return render(request, 'main/hunter/home.html', context)
	return redirect('landing')

#General hunter initial home view
def hunter_view(request, prospect=None):
	if request.user.is_authenticated:
		is_classified(request)
		if is_hunter(request):
			user = User.objects.get(pk=prospect)
			prospect = ProspectProfile.objects.get(prospect=user)
			education = ProspectEducation.objects.filter(prospect=user)
			experience = ProspectExperience.objects.filter(prospect=user)
			snippets = ProspectCodeSnippet.objects.filter(prospect=user)
			context = {
				'prospect': prospect,
				'education': education,
				'experience': experience,
				'snippets': snippets
			}
		return render(request, 'main/hunter/prospect.html', context)
	return redirect('landing')

#Allows for smtp request of hunter to prospect
def hunter_message(request, prospect=None):
	if request.user.is_authenticated:
		is_classified(request)
		if is_hunter(request):
			if request.method == "POST":
				form = ContactForm(request.POST)
				if form.is_valid():
					data = form.cleaned_data
					
					subject = 'myACEportrait - Message from '+str(request.user.username)
					message = data['message']
					from_email = str(request.user.email)
					prospect = User.objects.get(pk=prospect)
					recipients = [prospect.email]
					
					send_mail(subject, message, from_email, recipients, fail_silently=False)
					return redirect('hunter_home')
			else:
				form = ContactForm()
			context = {
				'form': form
			}
			return render(request, 'main/hunter/send_mail.html', context)

# Prospect Views
def prospect_home(request):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			try:
				profile = ProspectProfile.objects.get(prospect=request.user)
			except ProspectProfile.DoesNotExist:
				return redirect('/p/profile/create')
			snippets = ProspectCodeSnippet.objects.filter(prospect=request.user).order_by('-date_created')
			education = ProspectEducation.objects.filter(prospect=request.user).order_by('-date_created')
			experience = ProspectExperience.objects.filter(prospect=request.user).order_by('-date_created')
			context = {
				'profile': profile,
				'snippets': snippets,
				'education': education,
				'experience': experience
			}
			return render(request, 'main/prospect/home.html', context)
	return redirect('landing')

#New prospect request to add profile
def prospect_add_profile(request):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			if request.method == 'POST':
				form = ProspectProfileForm(request.POST)
				if form.is_valid():
					form = form.save(commit=False)
					form.prospect = request.user
					form.save()
					return redirect('prospect_home')
			else:
				form = ProspectProfileForm()
			context = {
				'form': form
			}
			return render(request, 'main/prospect/add_profile.html', context)
	return redirect('landing')

#Prospect altering of existing saved profile config, alters database of conatined propsect user data
def prospect_edit_profile(request):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			profile = ProspectProfile.objects.get(prospect=request.user)
			if request.method == 'POST':
				form = ProspectProfileForm(request.POST, instance=profile)
				if form.is_valid():
					form.save()
					return redirect('prospect_home')
			else:
				form = ProspectProfileForm(instance=profile)
			context =  {
				'form': form
			}
			return render(request, 'main/prospect/add_profile.html', context)

#Allow prospect to add example of produced code
def prospect_add_snippet(request):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			if request.method == 'POST':
				form = ProspectCodeSnippetForm(request.POST)
				if form.is_valid():
					form = form.save(commit=False)
					form.prospect = request.user
					form.save()
					return redirect('prospect_home')
			else:
				form = ProspectCodeSnippetForm()
			context = {
				'form': form
			}
			return render(request, 'main/prospect/add_snippet.html', context)
	return redirect('landing')

#Allow prospect to edit exitsing snippet saved to db
def prospect_edit_snippet(request, snippet=None):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			snippet = ProspectCodeSnippet.objects.get(pk=snippet)
			if snippet.prospect == request.user:
				if request.method == 'POST':
					form = ProspectCodeSnippetForm(request.POST, instance=snippet)
					if form.is_valid():
						form.save()
						return redirect('prospect_home')
				else:
					form = ProspectCodeSnippetForm(instance=snippet)
				context = {
					'form': form
				}
				return render(request, 'main/prospect/add_snippet.html', context)
	return redirect('landing')

#Bye bye snippet
def prospect_remove_snippet(request, snippet=None):
	if request.user.is_authenticated:
		is_classified(request)
		snippet = ProspectCodeSnippet.objects.get(pk=snippet)
		if snippet.prospect == request.user:
			snippet.delete()
			#ProspectCodeSnippet.objects.get(pk=snippet).delete()
		return redirect('prospect_home')
	return redirect('landing')

#See above
def prospect_add_education(request):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			if request.method == 'POST':
				form = ProspectEducationForm(request.POST)
				if form.is_valid():
					form = form.save(commit=False)
					form.prospect = request.user
					form.save()
					return redirect('prospect_home')
			else:
				form = ProspectEducationForm()
			context = {
				'form': form
			}
			return render(request, 'main/prospect/add_education.html', context)
	return redirect('landing')

#See above
def prospect_edit_education(request, education=None):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			education = ProspectEducation.objects.get(pk=education)
			if education.prospect == request.user:
				if request.method == 'POST':
					form = ProspectEducationForm(request.POST, instance=education)
					if form.is_valid():
						form = form.save(commit=False)
						form.prospect = request.user
						form.save()
						return redirect('prospect_home')
				else:
					form = ProspectEducationForm(instance=education)
				context = {
					'form': form
				}
				return render(request, 'main/prospect/add_education.html', context)
	return redirect('landing')

#See above
def prospect_remove_education(request, education=None):
	if request.user.is_authenticated:
		is_classified(request)
		education = ProspectEducation.objects.get(pk=education)
		if education.prospect == request.user:
			education.delete()
			#ProspectEducation.objects.get(pk=education).delete()
		return redirect('prospect_home')
	return redirect('landing')

#See above
def prospect_add_experience(request):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			if request.method == 'POST':
				form = ProspectExperienceForm(request.POST)
				if form.is_valid():
					form = form.save(commit=False)
					form.prospect = request.user
					form.save()
					return redirect('prospect_home')
			else:
				form = ProspectExperienceForm()
			context = {
				'form': form
			}
			return render(request, 'main/prospect/add_experience.html', context)
	return redirect('landing')

#See above
def prospect_edit_experience(request, experience=None):
	if request.user.is_authenticated:
		is_classified(request)
		if not is_hunter(request):
			experience = ProspectEducation.objects.get(pk=experience)
			if education.prospect == request.user:
				if request.method == 'POST':
					form = ProspectExperienceForm(request.POST, instance=experience)
					if form.is_valid():
						form = form.save(commit=False)
						form.prospect = request.user
						form.save()
						return redirect('prospect_home')
				else:
					form = ProspectExperienceForm(instance=experience)
				context = {
					'form': form
				}
				return render(request, 'main/prospect/add_experience.html', context)
	return redirect('landing')

#See above
def prospect_remove_experience(request, experience=None):
	if request.user.is_authenticated:
		is_classified(request)
		experience = ProspectExperience.objects.get(pk=education)
		if experience.prospect == request.user:
			experience.delete()
			#ProspectExperience.objects.get(pk=education).delete()
		return redirect('prospect_home')
	return redirect('landing')
