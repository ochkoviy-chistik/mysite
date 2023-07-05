from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from app.models import Doc


# Create your models here.


class UserManager (BaseUserManager):
    def create_user(self, email, username, last_name, first_name,
                    avatar=settings.DEFAULT_AVATAR, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('У пользователя должен быть адрес электронной почты!')

        if not username:
            raise ValueError('У пользователя должен быть ник!')

        if not last_name or not first_name:
            raise ValueError('Пользователь должен указать имя и фамилию!')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            avatar=avatar,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, username, last_name, first_name,
                         password, avatar=settings.DEFAULT_AVATAR):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            avatar=avatar,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, last_name, first_name,
                         password, avatar=settings.DEFAULT_AVATAR):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            avatar=avatar,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User (AbstractBaseUser):
    objects = UserManager()

    email = models.EmailField(
        verbose_name='адресс электронной почты',
        max_length=255,
        unique=True
    )
    username = models.CharField(
        verbose_name='ник',
        max_length=30,
        unique=True
    )
    avatar = models.ImageField(
        verbose_name='Avatar',
        default=settings.DEFAULT_AVATAR,
        upload_to=settings.AVATARS_UPLOAD_PATH,
        blank=False,
    )
    first_name = models.CharField(
        verbose_name='ваше имя',
        max_length=30
    )
    last_name = models.CharField(
        verbose_name='вашу фамилию',
        max_length=30
    )
    bookmarks = models.ManyToManyField(
        Doc,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return f'{self.last_name} {self.first_name}'

    def get_email(self):
        return self.email

    def get_short_name(self):
        return self.username

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return True

    @property
    def is_staff(self):
        """
        Is the user a member of staff?
        """
        return self.staff

    @property
    def is_admin(self):
        """
        Is the user an admin member?
        """
        return self.admin
