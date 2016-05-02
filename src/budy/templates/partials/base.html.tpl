{% extends "admin/layout.static.html.tpl" %}
{% block htitle %}{{ own.description }} / {% block title %}{% endblock %}{% endblock %}
{% block body_class %}{{ super() }} wide{% endblock %}
{% block head %}
    {{ super() }}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename = 'css/layout.css') }}" />
    <script type="text/javascript" src="{{ url_for('static', filename = 'js/main.js') }}"></script>
{% endblock %}
