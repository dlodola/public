
<div>
{% for post in site.posts %}
    <div class="blog"><img alt="lst" src="{{ site.url }}assets/images/jamie-lee-grady-4xQYT2RX2J8-unsplash.jpg" />
        {{ post.excerpt }}</div>
{% endfor %}
</div>
