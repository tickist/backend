#-*- coding: utf-8 -*-
from django.conf.urls import include, url
from .sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _
#admin.autodiscover()
from users.views import  UserTagsViewSet
from dashboard.lists.views import ListViewSet
from users.views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



router = DefaultRouter()
router.register(r'tag', UserTagsViewSet, base_name="tag")
router.register(r'project', ListViewSet, base_name="list")
router.register(r'user', UserViewSet)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^api/', include('dashboard.tasks.urls')),

    url(r'^api/', include('users.login.urls')),
    url(r'^api/', include('log_errors.urls')),
    url(r'^api/', include('statistics.urls')),

    url(r'^api/', include('users.registration.urls')),
    url(r'^api/', include('users.urls')),
    url(r'^api/', include('users.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
    url(r'^robots\.txt', include('robots.urls')),
    url('', include('social_django.urls', namespace='social')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #JOT
    url(r'^api/api-token-auth/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/api-token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^api/', include(router.urls)),
    url(r'^', include('emails.urls', namespace="emails"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
