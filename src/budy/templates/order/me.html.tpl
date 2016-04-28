{% extends "partials/internal.html.tpl" %}
{% block title %}Orders{% endblock %}
{% block name %}Orders{% endblock %}
{% block content %}
    <div class="quote">
        We're only showing your orders below.
    </div>
    <ul class="repos">
        {% for order in orders %}
            <li>
                <a href="#">{{ order.ident }}</a>
                <div class="clear"></div>
            </li>
        {% endfor %}
    </ul>
{% endblock %}
