{% extends "partials/base.html.tpl" %}
{% block links %}
    {% if link == "repos" %}
        <a href="{{ url_for('order.me') }}" class="active">orders</a>
    {% else %}
        <a href="{{ url_for('order.me') }}">orders</a>
    {% endif %}
{% endblock %}
