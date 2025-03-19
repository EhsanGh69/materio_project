from django.db import models

from account.models import User


class Notification(models.Model):
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifs', verbose_name='گیرنده پیام')
    subject = models.CharField(max_length=250, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    seen = models.BooleanField(default=False, verbose_name='مشاهده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='زمان ویرایش')

    class Meta:
        verbose_name = 'پیام ادمین'
        verbose_name_plural = 'پیام های ادمین'

    def __str__(self):
        return f'{self.reciever} - {self.subject}'
    

class Ticket(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tickets', verbose_name='فرستنده تیکت')
    title = models.CharField(max_length=250, verbose_name='عنوان')
    body = models.TextField(verbose_name='متن تیکت')
    answered = models.BooleanField(default=False, verbose_name='پاسخ داده شده')
    isAnswer = models.BooleanField(default=False, verbose_name='پاسخ تیکت')
    main = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                             blank=True, related_name='answer', verbose_name='تیکت اصلی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='زمان ویرایش')
    
    class Meta:
        verbose_name = 'تیکت کاربر'
        verbose_name_plural = 'تیکت های کاربران'

    def __str__(self):
        return f'{self.sender} - {self.title}'


