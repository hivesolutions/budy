{% extends "admin/layout.static.html.tpl" %}
{% block htitle %}{{ own.description }} / {% block title %}{% endblock %}{% endblock %}
{% block head %}
    {{ super() }}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename = 'css/layout.css') }}" />
    <script type="text/javascript" src="{{ url_for('static', filename = 'js/main.js') }}"></script>
{% endblock %}
{% block links %}
    {% if link == "repos" %}
        <a href="{{ url_for('repo.list') }}" class="active">orders</a>
    {% else %}
        <a href="{{ url_for('repo.list') }}">orders</a>
    {% endif %}
{% endblock %}
