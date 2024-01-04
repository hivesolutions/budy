{% extends "partials/base.html.tpl" %}
{% block links %}
    {% if link == "repos" %}
        <a href="{{ url_for('order.me') }}" class="active">orders</a>
    {% else %}
        <a href="{{ url_for('order.me') }}">orders</a>
    {% endif %}
{% endblock %}
{% block footer %}
    <div class="footer-container">
        {% set copyright = owner.copyright|default(copyright, True)|default("Hive Solutions", True) %}
        {% set copyright_year = owner.copyright_year|default(copyright_year, True)|default("2014-2024", True) %}
        {% set copyright_url = owner.copyright_url|default(copyright_url, True)|default("http://hive.pt", True) %}
        &copy; Copyright {{ copyright_year }} by
        {% if copyright_url %}
            <a href="{{ copyright_url }}">{{ copyright }}</a>.<br/>
        {% else %}
            <span>{{ copyright }}</span>.<br/>
        {% endif %}
        {% if session.username %}<span>{{ session.username }}</span> // <a href="{{ url_for('base.signout') }}">logout</a><br/>{% endif %}
    </div>
{% endblock %}
