---
layout: default
---

<!-- <h1>Articles</h1>

--- -->

<div>
{% for post in site.posts %}
    {% unless post.draft %}
    <div class="blog-header">
        <a href="{{ site.url }}{{ post.url }}">
            <img alt="lst" class="blog-header" src="{{ site.url }}assets/images/{{ post.image }}" width="100%"/>
        </a>
    </div>
    <div class="blog-body"><h1><a href="{{ site.url }}{{ post.url }}">{{ post.title }}</a></h1>
    {{ post.excerpt }}
    <p><a href="{{ site.url }}{{ post.url }}"><i>read more...</i></a></p>
    {% assign prefix = "" %}
    {% if post.tags != empty %}
        <small>tags: <em>
        {% for tag in post.tags %}{{ prefix }}<a href="{{ site.url }}/tags#{{ tag }}">{{ tag }}</a>{% assign prefix = "&nbsp;|&nbsp;" %}{% endfor %}
        </em></small>
    {% endif %}</div>
    <div class="blog-footer"><small>by: {{ post.author | "author" }}</small> | <small>posted on {{ post.date | date: "%-d %B %Y" }}</small></div>
    {% endunless %}
{% endfor %}
</div>

---
