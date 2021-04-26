---
layout: default
---

<h1>Articles</h1>

---

<div>
{% for post in site.posts %}
    {% if post.draft %}
    <div class="blog-header">
        <a href="{{ site.url }}{{ post.url }}">
            <img alt="lst" class="blog-header" src="{{ site.url }}assets/images/{{ post.image }}" width="100%"/>
        </a>
    </div>
    <div class="blog-body"><h1><a href="{{ site.url }}{{ post.url }}">{{ post.title }}</a></h1>
    {{ post.excerpt }}
    <p><a href="{{ site.url }}{{ post.url }}"><i>read more...</i></a></p>
    {% if post.tags != empty %}
        <small>tags: <em>{{ post.tags | join: "</em> - <em>" }}</em></small>
    {% endif %}</div>
    <div class="blog-footer"><small>by: {{ post.author | "author" }}</small> | <small>posted on {{ post.date | date: "%-d %B %Y" }}</small></div>
    {% endif %}
{% endfor %}
</div>

---
