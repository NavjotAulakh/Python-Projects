from django.urls import path, include
from . import views

urlpatterns = [
	# Generic Views
	path('', views.landing, name='landing'),
	path('accounts/signup/', views.signup, name='signup'),
	path('accounts/type/', views.choose_type, name='choose_type'),
	# Hunter Views
	path('h/home', views.hunter_home, name='hunter_home'),
	path('h/prospect/<int:prospect>', views.hunter_view, name='hunter_view'),
	path('h/prospect/<int:prospect>/like', views.hunter_like, name='hunter_like'),
	path('h/prospect/<int:prospect>/dislike', views.hunter_dislike, name='hunter_dislike'),
	path('h/prospect/<int:prospect>/message', views.hunter_message, name='hunter_message'),
	# Prospect views
	path('p/home', views.prospect_home, name='prospect_home'),
	# Prospect Profile
	path('p/profile/create', views.prospect_add_profile, name='prospect_add_profile'),
	path('p/profile/edit', views.prospect_edit_profile, name='prospect_edit_profile'),
	# Prospect Education
	path('p/education/add', views.prospect_add_education, name='prospect_add_education'),
	path('p/education/edit/<int:education>', views.prospect_edit_education, name='prospect_edit_education'),
	path('p/education/remove/<int:education>', views.prospect_remove_education, name='prospect_remove_education'),
	# Prospect Experience
	path('p/experience/add', views.prospect_add_experience, name='prospect_add_experience'),
	path('p/experience/edit/<int:experience>', views.prospect_edit_experience, name='prospect_edit_experience'),
	path('p/experience/remove/<int:experience>', views.prospect_remove_experience, name='prospect_remove_experience'),
	# Prospect Snippets
	path('p/snippet/add', views.prospect_add_snippet, name='prospect_add_snippet'),
	path('p/snippet/edit/<int:snippet>', views.prospect_edit_snippet, name='prospect_edit_snippet'),
	path('p/snippet/remove/<int:snippet>', views.prospect_remove_snippet, name='prospect_remove_snippet')
]
