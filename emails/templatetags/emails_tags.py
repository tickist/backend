#-*- coding: utf-8 -*-
from django import template
from django.template import Node
from django.template import defaulttags
from django import template
from django.utils.safestring import mark_safe
import random


register = template.Library()

"""
Example Usage in the template:

<p>{{ email|hide_email }}<br />
{% hide_email "name@example.com" "John Smith" %}</p>

{{ text_block|hide_all_emails|safe }}

All hidden emails are rendered as a hyperlink that is protected by
javascript and an email and name that are encoded randomly using a
hex digit or a decimal digit for each character.

Example of how a protected email is rendered:

<noscript>(Javascript must be enabled to see this e-mail address)</noscript>
<script type="text/javascript">// <![CDATA[
	document.write('<a href="mai'+'lto:&#106;&#x6f;&#x68;&#x6e;&#x40;&#101;&#120;&#97;&#109;&#x70;&#108;&#x65;&#46;&#x63;&#111;&#109;">&#74;&#111;&#104;&#110;&#x20;&#83;&#x6d;&#x69;&#x74;&#104;</a>')
// ]]></script>
"""

# snagged this function from http://www.djangosnippets.org/snippets/216/
def encode_string(value):
	e_string = ""
	for a in value:
		type = random.randint(0,1)
		if type:
			en = "&#x%x;" % ord(a)
		else:
			en = "&#%d;" % ord(a)
		e_string += en
	return e_string


def HideEmail(email, name=None):
	name        = name or email
	mailto_link = u'<a href="mai\'+\'lto:%s">%s</a>' % (encode_string(email), encode_string(name))

	return u"\n<noscript>(Javascript must be enabled to see this e-mail address)</noscript>\n" \
	       + '<script type="text/javascript">// <![CDATA['+ " \n \tdocument.write('%s')\n \t// ]]></script>\n" % (mailto_link)



@register.filter("hide_email")
def hide_email(email, name=None):
	name  = name or email
	value = HideEmail(email, name)
	return mark_safe(value)

