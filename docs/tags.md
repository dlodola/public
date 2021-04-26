---
layout: default
---

{% assign alltags = "" %}
{% for post in site.posts %}
    {% assign tags = post.tags | join: "," %}
    {% assign alltags = alltags | append: tags | append: "," %}

{% endfor %}

{% assign tags = alltags | split: "," | uniq %}

<p>
{% assign taglist = "" %}
{% for tag in tags %}
    <a href="#{{ tag }}">{{ tag }}</a> &ndash; 
{% endfor %}
</p>