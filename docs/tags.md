---
layout: default
---

{% assign alltags = "" %}
{% for post in site.posts %}
    {% assign tags = post.tags | join: "," %}
    {% assign alltags = alltags | append: tags | append: "," %}

{% endfor %}

{% assign tags = alltags | split: "," | uniq %}

## Tags
---
<p>
{% assign taglist = "" %}
{% for tag in tags %}
    <a href="#{{ tag }}">{{ tag }}</a> 
{% endfor %}
</p>


{% for tag in tags %}

#### {{ tag }}
<ul>
    {% for post in site.posts %}
        {% if post.tags contains tag %}
            <li><a href="{{ site.url }}{{ post.url }}">
                {{ post.date | date: "%-d %B %Y" }} &em;
                {{ post.title }}</a></li>
        {% endif %}
    {% endfor %}
</ul>
{% endfor %}

---