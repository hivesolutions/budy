{% extends "partials/internal.html.tpl" %}
{% block title %}Orders{% endblock %}
{% block name %}Orders{% endblock %}
{% block content %}
    <table class="table-full orders">
        {% for order in orders %}
            <tr>
                <td>{{ order.reference }}</td>
                <td>{{ order.email }}</td>
                <td>{{ order.status }}</td>
                <td>{{ order.total }}</td>
                <td>
                    {% if order.status == "waiting_payment" %}
                        <a class="link link-confirm" href="{{ url_for('order.mark_paid', key = order.key) }}"
                           data-message="Are you really sure you want to confirm payment for [[{{ order.reference }}]] ?">mark paid</a>
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
    </table>
{% endblock %}
