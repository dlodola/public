
<div>
{% for post in site.posts %}
    <div class="blog-header"><img alt="lst" src="{{ site.url }}assets/images/jamie-lee-grady-4xQYT2RX2J8-unsplash.jpg" width="100%"/></div>
    <div class="blog-body">{{ post.excerpt }}
    {% if page.tags %}
        <small>tags: <em>{{ post.tags | join: "</em> - <em>" }}</em></small>
    {% endif %}</div>
    <div class="blog-footer"><small>{{ post.author | by: "author" }}</small> | <small>{{ post.date | date: "%-d %B %Y" }}</small></div>
{% endfor %}
</div>

