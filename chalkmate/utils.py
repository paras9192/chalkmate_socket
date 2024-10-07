from rest_framework import status
import requests
from django.core.cache import cache
# from apps.translations.utils import TRANSLATION_MODEL_COLUMNS
# from apps.translations.models import Language
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

LOGGEER = settings.LOGGEER
GOOGLE_TRANSLATION_BASE_URL = settings.GOOGLE_TRANSLATION_BASE_URL
GOOGLE_TRANSLATION_API_KEY = settings.GOOGLE_TRANSLATION_API_KEY
USE_TRANSLATE = settings.USE_TRANSLATE

class ListSiblingSerializerClass (object):
    def to_representation(self, instance):
        s_ret = super().to_representation(instance)
        request =  self.context.get('request')
        model = instance._meta.verbose_name
        context = {
            'request': request,
            'model': model,
        }
        for col in TRANSLATION_MODEL_COLUMNS[model]:
            s_ret[col] = hashed_translate_cache_hoc(context=context, text=s_ret[col], column=col, uid=instance.id)
        return s_ret

def custom_success_response(serialized_data, message='success',count=None, status=status.HTTP_200_OK, headers=None, **kwargs,):
    data = {}
    data['data'] = serialized_data
    if count is not None:
        data['count'] = count
    for key, value in kwargs.items():
        data[key] = value
    data['status'] = '1'
    return JsonResponse(data, status=status, headers=headers)

def generate_cache_key (target, instance, column):
    # To generate cache key 
    LOGGEER.debug("generate_cache_key ")
    return f'{target}-{instance._meta.db_table}-{column}-{instance.id}'

def update_cache (text, target, instance, column):
    #To update cache 
    LOGGEER.debug("update_cache "+ column )
    cache_key = generate_cache_key(target, instance, column)
    cache.set(cache_key, text,60*15)

def delete_cache (target, instance, column):
    LOGGEER.debug("delete_cache "+ column )
    cache_key = generate_cache_key(target, instance, column)
    cache.delete(cache_key)

def cache_decorator(f):
    def inner (*args, **kwargs):
            target = args[1]
            instance = args[2]
            column = args[3]
            cached_key = generate_cache_key(target, instance, column)
            cached_value = cache.get(cached_key)
            if cached_value is not None: return {'translated_text': cached_value}
            return f(*args, **kwargs)
    return inner

def translate_text_single (text, target):
    "To translate text (see translations in POSTS)"
    if USE_TRANSLATE=="TRUE":
        response = requests.get(f"{GOOGLE_TRANSLATION_BASE_URL}/language/translate/v2?key={GOOGLE_TRANSLATION_API_KEY}&q={text}&target={target}")
        res_json = response.json()
        translated_text = res_json["data"]["translations"][0]["translatedText"]
        return {'translated_text': translated_text}
    else: return {'translated_text': "Translation is not in use"}

def detect_text_language (text):
    if USE_TRANSLATE=="TRUE":
        response = requests.get(f"{GOOGLE_TRANSLATION_BASE_URL}/language/translate/v2/detect?key={GOOGLE_TRANSLATION_API_KEY}&q={text}")
        res_json = response.json()
        language_detected = res_json["data"]["detections"][0][0]["language"]
        return {'language_detected': language_detected}
    else: return {'language_detected': "not-en"}

@cache_decorator
def translate_text_fun (text, target, instance , column ):
    LOGGEER.debug("translate_text_fun "+ column )
    if USE_TRANSLATE=="TRUE":
        response = requests.get(f"{GOOGLE_TRANSLATION_BASE_URL}/language/translate/v2?key={GOOGLE_TRANSLATION_API_KEY}&q={text}&target={target}")
        res_json = response.json()
        translated_text = res_json["data"]["translations"][0]["translatedText"]
        update_cache(translated_text, target, instance, column)
        return {'translated_text': translated_text}
    else: 
        update_cache("Translation is not in use", target, instance, column)
        return {'translated_text': "Translation is not in use"}

def translate_text(context,re,transColumn, instance):
    LOGGEER.debug("translate_text "+ str(context['request'].method) )
    if context['request'].method == 'GET':
        if context['target'] == "No_translation": return re
        for key in TRANSLATION_MODEL_COLUMNS[transColumn]:
            LOGGEER.debug("translate_text in GET request - " + transColumn + " re[key]- " + str(re[key]))
            translated_text = translate_text_fun(re[key], context['target'], instance, key)
            if translated_text["translated_text"] is not None:
                re[key] = translated_text["translated_text"]
    else:
        language_obj = Language.objects.all()
        for key in TRANSLATION_MODEL_COLUMNS[transColumn]:
            if key in context['request'].data.keys():
                lang = detect_text_language(re[key])['language_detected']
                for obj in language_obj:
                    delete_cache(obj.language_code, instance, key)
                if lang is not None:
                    update_cache(re[key], lang, instance, key)
    LOGGEER.debug("translate_text Responce [No Error] -"+ str(re) )
    return re

def update_object_response(message='success ok', status=status.HTTP_200_OK, headers=None):
    data = {}
    data['message'] = message
    data['status'] = '1'
    return JsonResponse(data, status=status, headers=headers)

# cache revamp
ttl = 60 * 15
def hashed_remove_translate_cache (model, column, uid):
    lang_objs = Language.objects.all()
    for lang_obj in lang_objs:
        key = hashed_key_generate(model, column, uid, lang_obj.language_code)
        cache.delete(key)

def hashed_target_language (target):
    if target is None:
        default_lang_obj = Language.objects.get(default=True) 
        return default_lang_obj.language_code
    if target == "No_translation": return target
    lang_obj = Language.objects.filter(language_code=target).last()
    if not lang_obj:
        return "No_translation"
    return lang_obj.language_code

def hashed_is_cached (key):
    cached_res = cache.get(key)
    if cached_res is not None:
        return cached_res
    return None

def hashed_set_cache (key, text):
    cache.set(key, text, ttl)

def hashed_key_generate (model, column, uid, lang):
    return f'{model}-{column}-{uid}-{lang}'

def hashed_translate_text (text, lang):
    if USE_TRANSLATE=="TRUE":
        response = requests.get(f"{GOOGLE_TRANSLATION_BASE_URL}/language/translate/v2/?target={lang}&key={GOOGLE_TRANSLATION_API_KEY}&q={text}")
        res_json = response.json()
        translated_text = res_json["data"]["translations"][0]["translatedText"]
        return translated_text
    else: return text

def hashed_detect_text_language (text):
    if USE_TRANSLATE=="TRUE":
        response = requests.get(f"{GOOGLE_TRANSLATION_BASE_URL}/language/translate/v2/detect?key={GOOGLE_TRANSLATION_API_KEY}&q={text}")
        res_json = response.json()
        language_detected = res_json["data"]["detections"][0][0]["language"]
        return language_detected
    else: return "en"

def hashed_translate_and_cache (key, text, lang):
    t_text = hashed_translate_text(text, lang)
    hashed_set_cache(key, t_text)
    return t_text

def hashed_translate_cache_hoc (context, text=None, model=None, column=None, uid=None):
    if context['request'].method == 'GET':
        lang = hashed_target_language(context['request'].query_params.get('target'))
        if lang == 'No_translation': return text
        if model is None:
            model = context["model"]
        key = hashed_key_generate(model, column, uid, lang)
        res = hashed_is_cached(key)
        if res is not None: return res
        return hashed_translate_and_cache(key, text, lang)
    
    if uid is None:
        uid = context['request'].parser_context['kwargs']['pk']
    if model is None:
        model = context['model']
    for col in context['request'].data.keys():
        if col in TRANSLATION_MODEL_COLUMNS[model]:
            hashed_remove_translate_cache(model, col, uid)
    return text

