import hashlib

from django.core.mail import send_mail


def get_confirmation_code(username: str) -> str:
    """Возвращает код подтверждения."""
    md5_hash = hashlib.new('md5')
    md5_hash.update(username.encode())
    return md5_hash.hexdigest()


def send_confirmation_email(username: str, email: str) -> None:
    """Отправляет письмо с кодом подтверждения на указанный email."""
    code = get_confirmation_code(username)
    send_mail(
        subject='Регистрация на YaMDb',
        message=f'Ваш код подтверждения: {code}',
        from_email='YaMDb',
        recipient_list=[f'{email}'],
        fail_silently=True
    )
