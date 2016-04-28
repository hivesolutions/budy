{% extends "base.html.tpl" %}
{% block title %}Login{% endblock %}
{% block content %}
    <div class="login-panel">
        <h1>Login</h1>
        <h3>Sign in to continue to <strong>{{ own.description }}</strong></h3>
        <div class="quote error">
            {{ error }}
        </div>
        <form action="{{ url_for('base.login') }}" method="post" class="form">
            <input type="hidden" name="next" value="{{ next|default('', True) }}" />
            <div class="input">
                <input type="text" class="text-field small focus" name="username" value="{{ username }}"
                       placeholder="username" />
            </div>
            <div class="input">
                <input type="password" class="text-field small" name="password" placeholder="password" />
            </div>
            <div class="buttons">
                <span class="button medium button-color button-blue" data-submit="true">Login</span>
            </div>
        </form>
    </div>
{% endblock %}
