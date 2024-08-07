{% raw %}
# Templating

When rendering the Outcomes, AutoDocument will perform field substitution using the "curly brace" syntax: `{{ }}`. You don't need to add any special "field" objects or anything else into your Word Document Templates.

There are also a slew of other useful templating tools available, such as the curly brace + percent syntax, which denotes adding logic to the template. For example:

```html
{% if show_warning == 1 %}
Warning: surface is hot
{% endif %}
```

You also use the `{% %}` syntax when iterating over multi-records sources that have been set to a field:

```html
{% for item in purchases %}
{{ item.name }}: {{ item.quantity }} @ {{ item.price }} - Total Price: {{item.value}}
{% endfor %}
```

---

## Templating Engine

AutoDocument uses the powerful Jinja2 for templating, and so has access to all the wonderful features that Jinja2 has. See their [documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/) for more info.

---

## Microsoft Word

AutoDocument uses the fantastic [python-docx-template](https://github.com/elapouya/python-docx-template) library for templating in Microsoft Word. This uses Jinja2 under the hood so the syntax is the same no matter what Outcome you use, however it adds some other Word-specific tools to make working with it more convenient, like the `{%p %}` syntax for working with paragraphs. See their [documentation](https://docxtpl.readthedocs.io/en/latest/) for the full list of features.
{% endraw %}
