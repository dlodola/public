
<div>
{% for post in site.posts %}
    <div class="blog-header"><img alt="lst" src="{{ site.url }}assets/images/jamie-lee-grady-4xQYT2RX2J8-unsplash.jpg" width="100%"/></div>
    <div class="blog-body">{{ post.excerpt }}</div>
    <div class="blog-footer">by:</div>
{% endfor %}
</div>
