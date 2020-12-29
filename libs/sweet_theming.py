from flask import render_template


def render_themed_template(template_name, theme_type, **kwargs):
    if theme_type == 'admin':
        theme = 'appzia'
    return render_template(f'{theme_type}/themes/{theme}/{template_name}', **kwargs)


def themed_template(template_name, theme_type):
    if theme_type == 'admin':
        theme = 'appzia'
    elif theme_type == 'web':
        theme = 'sweet'
    return f'{theme_type}/themes/{theme}/{template_name}'
