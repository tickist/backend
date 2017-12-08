# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.core import management
from django.contrib.auth.models import User
import pickle
import random

import datetime
import string
from random import choice

DATABASE = 1  # 0- empty 1- small; 2- normal; 3- big; 4 - huge


class Random_gen():
    """
     Klasa wykorzystywana do generowania losowych danych
    """

    def __init__(self):
        # pobranie listy przykładowych imion, nazwisk, nicków
        self.email_domain = "@dydacto.com"
        self.hex_table = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.chars = string.ascii_letters + string.digits
        f = open("./commons/gen_test_data/list_name" , 'r')
        self.name_list = []
        line = f.readline().strip()
        while line != '':
            self.name_list.append(line)
            line = f.readline().strip()

        self.len_name_list = len(self.name_list)

        f = open(b"commons/gen_test_data/list_surname", "r")
        self.surname_list = []
        line = f.readline().strip()
        while line != '':
            self.surname_list.append(line)
            line = f.readline().strip()

        self.len_surname_list = len(self.surname_list)

        f =  open(b"commons/gen_test_data/list_nick", "r")
        self.nick_list = []
        line = f.readline().strip()
        while line != '':
            self.nick_list.append(line)
            line = f.readline().strip()

        self.len_nick_list = len(self.nick_list)

    def email_gen(self):
        """
        Funkcja generująca przykładowy adres email
        """
        nick = self.nick_gen()
        number = random.randint(0, 99)
        email = u"%s_%s@%s" % (nick, number, self.email_domain)
        return email

    def name_gen(self):
        """
        Funkcja generująca przykładowe imie
        """
        index = random.randint(0, self.len_name_list - 1)

        return self.name_list[index]

    def surname_gen(self):
        """
        Funkcja generująca przykładowe nazwisko
        """
        index = random.randint(0, self.len_surname_list - 1)
        return self.surname_list[index]

    def nick_gen(self):
        """
        Funkcja generujaca przykładowe nick
        """
        index = random.randint(0, self.len_nick_list - 1)
        sufix = ''.join([choice(self.chars) for i in range(5)])
        return self.nick_list[index] + "_" + sufix

    def zip_gen(self):
        """
        Funkcja generujaca kod pocztowy
        """
        zip_code = ''.join([choice(string.digits) for i in range(2)]) + "-" + ''.join(
            [choice(string.digits) for i in range(3)])
        return zip_code

    def school_name_gen(self):
        """
        Funkcja generujaca nazwy szkół
        """
        len_name = random.randint(4, 15)
        name = ''.join([choice(string.letters) for i in range(len_name)])
        return name

    def address_gen(self):
        """
        Funkcja generująca adresy

        """
        address_len = random.randint(5, 14)
        address = ''.join([choice(string.letters) for i in range(address_len)]) + " " + ''.join(
            [choice(string.digits) for i in range(2)])
        return address

    def city_gen(self):
        """
        Funckja generujaca losową nazwę miejscowości
        """
        city_len = random.randint(5, 14)
        city = ''.join([choice(string.letters) for i in range(city_len)])
        return city

    def phone_number_gen(self):
        """
        Funkcja generujaca numer telefonu  w formacie (XXX)YYYYYY albo (XX)YYYYYYY
        """
        tmp = random.randint(0, 1)
        if tmp:
            phone = '('.join([choice(string.digits) for i in range(3)]) + ")" + ''.join(
                [choice(string.digits) for i in range(6)])
        else:
            phone = '('.join([choice(string.digits) for i in range(2)]) + ")" + ''.join(
                [choice(string.digits) for i in range(7)])
        return phone

    def text_gen(self, len_max=None):
        """
        Funkcja generujaca tekst do textfields, generuje losowej długości tekst z wyrazów łacińskich,
        dodatkowo jako parametr ma maksymalną długość tekstu zwracanego
        """
        if len_max != None:
            while (len(sentence()) > len_max):
                pass

        return sentence()

    def mark_gen(self):
        """
        Funkcja generujaca liczbę całkowitę z przedziału od 1 do 6
        """

        return random.randint(1, 6)

    def timeField_gen(self, **kwargs):
        """
        Generates time object for TimeField's
        """
        today = datetime.datetime.now()
        return datetime.time(today.hour, today.minute, today.second)

    def iPAddressField_gen(self, **kwargs):
        """
        Generates a random IP Address
        """
        ip = str(random.randrange(0, 255)) + "." + str(random.randrange(0, 255)) + "." + str(
            random.randrange(0, 255)) + "." + str(random.randrange(0, 255))
        return ip

    def dateTimeField_gen(self, **kwargs):

        """ Generates datetime for DateTimeField's"""
        month = random.randint(1, 11)
        day = random.randint(1, 27)
        h = random.randint(1, 23)
        min = random.randint(1, 59)
        sec = random.randint(1, 59)
        if h < 10:
            h = "0" + str(h)
        if month < 10:
            month = "0" + str(month)
        if day < 10:
            day = "0" + str(day)
        if min < 10:
            min = "0" + str(min)
        if sec < 10:
            sec = "0" + str(sec)

        return "2010-%s-%s %s:%s:%s" % (month, day, h, min, sec)

    def website_gen(self):
        """ funkcja generuje losową stronę www"""
        website = "www."
        website += ''.join([choice(string.letters) for i in range(7)])
        website += ".pl"
        return website

    def raw_file_gen(self, file_raw=None):
        """
        Funkcja generuje losową zawartość pliku
        """
        file = ""
        if file_raw == None:
            file_raw = 1024
        for arg in range(file_raw):
            number = random.randint(0, len(self.hex_table) - 1)
            file += self.hex_table[number]
        return file

COMMON_P = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

WORDS = ('exercitationem', 'perferendis', 'perspiciatis', 'laborum', 'eveniet',
        'sunt', 'iure', 'nam', 'nobis', 'eum', 'cum', 'officiis', 'excepturi',
        'odio', 'consectetur', 'quasi', 'aut', 'quisquam', 'vel', 'eligendi',
        'itaque', 'non', 'odit', 'tempore', 'quaerat', 'dignissimos',
        'facilis', 'neque', 'nihil', 'expedita', 'vitae', 'vero', 'ipsum',
        'nisi', 'animi', 'cumque', 'pariatur', 'velit', 'modi', 'natus',
        'iusto', 'eaque', 'sequi', 'illo', 'sed', 'ex', 'et', 'voluptatibus',
        'tempora', 'veritatis', 'ratione', 'assumenda', 'incidunt', 'nostrum',
        'placeat', 'aliquid', 'fuga', 'provident', 'praesentium', 'rem',
        'necessitatibus', 'suscipit', 'adipisci', 'quidem', 'possimus',
        'voluptas', 'debitis', 'sint', 'accusantium', 'unde', 'sapiente',
        'voluptate', 'qui', 'aspernatur', 'laudantium', 'soluta', 'amet',
        'quo', 'aliquam', 'saepe', 'culpa', 'libero', 'ipsa', 'dicta',
        'reiciendis', 'nesciunt', 'doloribus', 'autem', 'impedit', 'minima',
        'maiores', 'repudiandae', 'ipsam', 'obcaecati', 'ullam', 'enim',
        'totam', 'delectus', 'ducimus', 'quis', 'voluptates', 'dolores',
        'molestiae', 'harum', 'dolorem', 'quia', 'voluptatem', 'molestias',
        'magni', 'distinctio', 'omnis', 'illum', 'dolorum', 'voluptatum', 'ea',
        'quas', 'quam', 'corporis', 'quae', 'blanditiis', 'atque', 'deserunt',
        'laboriosam', 'earum', 'consequuntur', 'hic', 'cupiditate',
        'quibusdam', 'accusamus', 'ut', 'rerum', 'error', 'minus', 'eius',
        'ab', 'ad', 'nemo', 'fugit', 'officia', 'at', 'in', 'id', 'quos',
        'reprehenderit', 'numquam', 'iste', 'fugiat', 'sit', 'inventore',
        'beatae', 'repellendus', 'magnam', 'recusandae', 'quod', 'explicabo',
        'doloremque', 'aperiam', 'consequatur', 'asperiores', 'commodi',
        'optio', 'dolor', 'labore', 'temporibus', 'repellat', 'veniam',
        'architecto', 'est', 'esse', 'mollitia', 'nulla', 'a', 'similique',
        'eos', 'alias', 'dolore', 'tenetur', 'deleniti', 'porro', 'facere',
        'maxime', 'corrupti')

COMMON_WORDS = ('lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur',
        'adipisicing', 'elit', 'sed', 'do', 'eiusmod', 'tempor', 'incididunt',
        'ut', 'labore', 'et', 'dolore', 'magna', 'aliqua')

def sentence():
    """
    Returns a randomly generated sentence of lorem ipsum text.

    The first word is capitalized, and the sentence ends in either a period or
    question mark. Commas are added at random.
    """
    # Determine the number of comma-separated sections and number of words in
    # each section for this sentence.
    sections = [' '.join(random.sample(WORDS, random.randint(3, 12))) for i in range(random.randint(1, 5))]
    s = ', '.join(sections)
    # Convert to sentence case and add end punctuation.
    return '%s%s%s' % (s[0].upper(), s[1:], random.choice('?.'))

def paragraph():
    """
    Returns a randomly generated paragraph of lorem ipsum text.

    The paragraph consists of between 1 and 4 sentences, inclusive.
    """
    return ' '.join([sentence() for i in range(random.randint(1, 4))])

def paragraphs(count, common=True):
    """
    Returns a list of paragraphs as returned by paragraph().

    If `common` is True, then the first paragraph will be the standard
    'lorem ipsum' paragraph. Otherwise, the first paragraph will be random
    Latin text. Either way, subsequent paragraphs will be random Latin text.
    """
    paras = []
    for i in range(count):
        if common and i == 0:
            paras.append(COMMON_P)
        else:
            paras.append(paragraph())
    return paras

def words(count, common=True):
    """
    Returns a string of `count` lorem ipsum words separated by a single space.

    If `common` is True, then the first 19 words will be the standard
    'lorem ipsum' words. Otherwise, all words will be selected randomly.
    """
    if common:
        word_list = list(COMMON_WORDS)
    else:
        word_list = []
    c = len(word_list)
    if count > c:
        count -= c
        while count > 0:
            c = min(count, len(WORDS))
            count -= c
            word_list += random.sample(WORDS, c)
    else:
        word_list = word_list[:count]
    return ' '.join(word_list)
