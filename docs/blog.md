
<div>
{% for post in site.posts %}
    <div class="blog-header"><img alt="lst" src="{{ site.url }}assets/images/jamie-lee-grady-4xQYT2RX2J8-unsplash.jpg" width="100%"/></div>
    <div class="blog-body"><h1><a href="{{ site.url }}{{ post.url }}">{{ post.title }}</a></h1>
    {{ post.excerpt }}
    {% if post.tags %}
        <small>tags: <em>{{ post.tags | join: "</em> - <em>" }}</em></small>
    {% endif %}</div>
    <div class="blog-footer"><small>by: {{ post.author | "author" }}</small> | <small>posted on {{ post.date | date: "%-d %B %Y" }}</small></div>
{% endfor %}
</div>

