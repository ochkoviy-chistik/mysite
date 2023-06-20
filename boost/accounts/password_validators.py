import re
from difflib import SequenceMatcher

from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    exceeds_maximum_length_ratio,
    CommonPasswordValidator,
    MinimumLengthValidator,
    NumericPasswordValidator, get_default_password_validators,
)
from django.utils.translation import gettext as _, ngettext
from django.core.exceptions import (
    FieldDoesNotExist,
    ValidationError,
)


class RussianUserAttributeSimilarityValidator (UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                        password, self.max_similarity, value_part
                ):
                    continue
                if (
                        SequenceMatcher(a=password, b=value_part).quick_ratio()
                        >= self.max_similarity
                ):
                    try:
                        verbose_name = str(
                            user._meta.get_field(attribute_name).verbose_name
                        )
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("Пароль слишком похож на %(verbose_name)s."),
                        code="password_too_similar",
                        params={"verbose_name": verbose_name},
                    )


class RussianCommonPasswordValidator (CommonPasswordValidator):
    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Этот пароль слишком распространен."),
                code="password_too_common",
            )


class RussianMinimumLengthValidator (MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Этот пароль слишком короткий. Он должен содержать не менее "
                    "%(min_length)d символов.",
                    "Этот пароль слишком короткий. Он должен содержать не менее "
                    "%(min_length)d символов.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )


class RussianNumericPasswordValidator (NumericPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Этот пароль полностью числовой."),
                code="password_entirely_numeric",
            )


def password_valid(password, user=None, password_validators=None):
    errors = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.append(error)

    return errors
