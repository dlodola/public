---
layout: default
---

{% assign alltags = "" %}
{% for post in site.posts %}
    {% assign tags = post.tags | join: "," %}
    {% assign alltags = alltags | append: tags %}

{% endfor %}

<p>{{ alltags }}</p>