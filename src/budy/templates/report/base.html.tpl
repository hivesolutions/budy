<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{% block title %}{% endblock %} - Budy</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap" />
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename = 'css/report.css') }}" />
    </head>
    <body>
        <div class="report">
            <header class="report-header">
                {% block report_status %}{% endblock %}
                {% block report_header %}{% endblock %}
                {% block report_timestamp %}{% endblock %}
            </header>
            <section class="report-section">
                <h2 class="report-section-title">{% block report_meta_title %}Metadata{% endblock %}</h2>
                <dl class="report-dl">
                    {% block report_meta %}{% endblock %}
                </dl>
            </section>
            {% block report_body %}{% endblock %}
            <footer class="report-footer">
                {% block report_footer %}{% endblock %}
            </footer>
        </div>
    </body>
</html>
