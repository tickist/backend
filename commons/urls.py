from django.conf import settings
from dashboard.tasks.models import choices_priority, choices_repeat, choices_type_finish_date, choices_from_repeating
from dashboard.lists.models import color_list, choices_default_finish_date


def javascript_settings():
    repeat_options_list = []
    from_repeating_options_list = []
    type_finish_date_options_list = []
    color_list_js = []
    choices_default_finish_date_js = []
    for repeat in choices_repeat:
        repeat_options_list.append({'id': repeat[0], 'name': repeat[1].encode(), "name_of_extension": repeat[2].encode()})
    for repeat in choices_from_repeating:
        from_repeating_options_list.append({'id': repeat[0], 'name': repeat[1].encode()})
    for type_finish_date in choices_type_finish_date:
        type_finish_date_options_list.append({'id': type_finish_date[0], 'name': type_finish_date[1].encode()})
    for color in color_list:
        color_list_js.append(color[0])
    for date in choices_default_finish_date:
        choices_default_finish_date_js.append({'id': date[0], 'name': date[1]})

    js_conf = {
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
            'REPEATING_OPTIONS': repeat_options_list,
            'COLOR_LIST': color_list_js,
            'COLOR_LIST_DEFAULT': settings.DEFAULT_COLOR_LIST,
            'FROM_REPEATING_OPTIONS': from_repeating_options_list,
            'TYPE_FINISH_DATE_OPTIONS': type_finish_date_options_list,
            'CHOICES_DEFAULT_FINISH_DATE': choices_default_finish_date_js,
            'Google_plus_client_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
            'Google_plus_scope': ' '.join(settings.SOCIAL_AUTH_GOOGLE_OAUTH_SCOPE),
            'SOCIAL_AUTH_FACEBOOK_KEY': settings.SOCIAL_AUTH_FACEBOOK_KEY,
            'FACEBOOK_FANPAGE': settings.FACEBOOK_FANPAGE,
            'GOOGLE_PLUS': settings.GOOGLE_PLUS,
            'TWITTER': settings.TWITTER

    }
    return js_conf
