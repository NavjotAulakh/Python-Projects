from django.contrib import admin

from main.models import UserProfile, ProspectProfile, ProspectCodeSnippet, ProspectEducation, ProspectExperience

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ProspectProfile)
admin.site.register(ProspectCodeSnippet)
admin.site.register(ProspectEducation)
admin.site.register(ProspectExperience)