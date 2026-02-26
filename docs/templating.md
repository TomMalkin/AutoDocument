{% raw %}
# Templating

When rendering the Outcomes, AutoDocument will perform field substitution using the "curly brace" syntax: `{{ }}`. You don't need to add any special "field" objects or anything else into your Word Document Templates.

Simple add `{{ field }}` anywhere at it will be replaced by the value of that field when running the Workflow.

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

## Special Functions

### Inserting Images Inline

New in 0.5.3+

2 special functions have been added that can be used in the template:

_image_url() and _image_file()

#### _image_url()

_image_url() is used to insert an image from a url:

```html
This is an image:

{{ _image_url("https://my.image.url.jpg")}}
```

You can also use any field from any previous source!

For example, if you have a form field with the name "my_image_url"

then you can use it like any variable:

```html
{{ _image_url(my_image_url) }}
```

Or if you have a csv that looks like:

```csv
url
https://my.image.1.jpg
https://my.image.2.jpg
https://my.image.3.jpg
```

If it has been loaded as a splitter, then:

```html
{{ _image_url(url) }}
```

Or if it has been loaded a Field (lets say you named it "photo_urls"):

```html
{% for record in photo_urls %}
{{ _image_url(record.url) }}
{% endfor %}
```

This will insert each image from the csv!


#### _image_file()

_image_file works in exactly the same way, except the expected argument is a path.

NOTE: The path is from the CONTAINER's PERSPECTIVE. So if you have an image saved to /my/shared/network/photo.jpg, but /my/shared/network has been mounted to /local_mount in the container, then you must give it /local_mount/photo.jpg

```html
{{ _image_file("/local_mount/photo.jpg")}}
```

```html
{% for record in my_files %}
{{ _image_file(record.path) }}
{% endfor %}
```

### Resizing

Both _image_url and _image_file has sizing available and optional:

set either width_mm, width_cm, or width_inches
set either height_mm, height_cm, or height_inches

{{ _image_url(url, width_cm=5, height_inches=2)}}


---

## Templating Engine

AutoDocument uses the powerful Jinja2 for templating, and so has access to all the wonderful features that Jinja2 has. See their [documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/) for more info.

---

## Microsoft Word

AutoDocument uses the fantastic [python-docx-template](https://github.com/elapouya/python-docx-template) library for templating in Microsoft Word. This uses Jinja2 under the hood so the syntax is the same no matter what Outcome you use, however it adds some other Word-specific tools to make working with it more convenient, like the `{%p %}` syntax for working with paragraphs. See their [documentation](https://docxtpl.readthedocs.io/en/latest/) for the full list of features.
{% endraw %}
