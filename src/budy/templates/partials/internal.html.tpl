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
        &copy; Copyright 2008-2017 by <a href="http://hive.pt">Hive Solutions</a>.<br/>
        {% if session.username %}<span>{{ session.username }}</span> // <a href="{{ url_for('base.signout') }}">logout</a><br/>{% endif %}
    </div>
{% endblock %}
