from django.contrib import admin
from django.urls import path
from script import views
from login import views as viewslogin
from payment import views as viewspay
from chat import views as viewschat
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.work,name='main'),
    path('about',views.about,name='about'),
    path('contact-us',views.contact,name='contact'),
    path('pricing',views.pricing,name='pricing'),
    path('dashboard',views.dashboard,name='dash'),
    path('main-data',views.data,name='data'),
    path('debt',views.debt,name='debt'),
    path('expense',views.expense,name='expense'),
    path('income',views.income,name='income'),
    path('lsexpense',views.lsexpense,name='lsexpense'),
    path('lsincome',views.lsincome,name='lsincome'),
    path('summary/<int:select>',views.summary,name='summary'),
    path('delete/<int:model>/<slug:the_slug>',views.delete,name='delete'),
    path('edit/<int:model>',views.edit,name='edit'),
    path('checkout',viewspay.checkout_page,name='checkout'),
    path('payment',viewspay.payment,name='payment'),
    path('loggin',viewslogin.login,name='login'),
    path('logout',viewslogin.logout,name='logout'),
    path('signup',viewslogin.signup,name='signup'),
    path('confirm',viewslogin.confirm,name='confirm'),
    path('changepass',viewslogin.changepass,name='changepass'),
    path('forgot',viewslogin.forgot,name='forgot'),
    path('chat', viewschat.chat_view, name='chats'),
    path('chat/<int:sender>/<int:receiver>', viewschat.message_view, name='chat'),
    path('api/messages/<int:sender>/<int:receiver>', viewschat.message_list, name='message-detail'),
    path('api/messages', viewschat.message_list, name='message-list'),
    path('api/users/<int:pk>', viewschat.user_list, name='user-detail'),
    path('api/users', viewschat.user_list, name='user-list'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATICFILES_DIRS)