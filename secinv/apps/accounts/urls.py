from django.conf.urls.defaults import patterns, url, include
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'accounts/index.html'},
        name='auth-login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'accounts/logout.html'},
        name='auth-logout'),
    url(r'^password/change/$',
        auth_views.password_change,
        name='auth-password-change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth-password-change-done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='auth-password-reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth-password-reset-confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth-password-reset-complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth-password-reset-done'),

)

