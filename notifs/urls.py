from django.urls import path

from . import views

app_name = 'notifs'

urlpatterns = [
    path('reject_post/<int:pk>', views.post_reject, name='reject_post'),
    path('remove_post/<int:pk>', views.remove_post, name='remove_post'),
    path('edit_reject_notif/<int:pk>', views.edit_reject_notif, name='edit_reject_notif'),

    path('all_comments/', views.all_comments, name='all_comments'),
    path('paginate_comments/', views.paginate_comments, name='paginate_comments'),
    path('accept_comment/<int:pk>', views.accept_comment, name='accept_comment'),
    path('remove_comment/<int:pk>', views.remove_comment, name='remove_comment'),

    path('persuit_ticket/<int:post_id>', views.persuit_ticket, name='persuit_ticket'),
    path('my_tickets/', views.my_tickets, name='my_tickets'),
    path('my_tickets_paginate/', views.my_tickets_paginate, name='my_tickets_paginate'),
    path('view_ticket/<int:pk>', views.view_my_ticket, name='view_my_ticket'),
    path('send_ticket/', views.send_ticket, name='send_ticket'),
    path('user_tickets/', views.user_tickets, name='user_tickets'),
    path('user_tickets_paginate/', views.user_tickets_paginate, name='user_tickets_paginate'),
    path('answer_ticket/<int:pk>', views.answer_ticket, name='answer_ticket'),
    path('remove_ticket/<int:pk>', views.remove_ticket, name='remove_ticket'),

    path('all_notifs/', views.all_notifs, name='all_notifs'),
    path('my_notifs/', views.all_notifs, name='my_notifs'),
    path('paginate_notifs/', views.paginate_notifs, name='paginate_notifs'),
    path('remove_notif/<int:pk>', views.remove_notif, name='remove_notif'),
    path('send_notif/', views.send_notif, name='send_notif'),
    path('view_notif/<int:pk>', views.view_notif, name='view_notif'),
]