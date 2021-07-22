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

{% for tag in tags %}
<div id="tag_{{ tag }}" class="tag">
<h4>{{ tag }}</h4>
<ul>
    {% for post in site.posts %}
        {% if post.tags contains tag %}
            <li><a href="{{ site.url }}{{ post.url }}">
                {{ post.date | date: "%-d %B %Y" }} &mdash;
                {{ post.title }}</a></li>
        {% endif %}
    {% endfor %}
</ul>
</div>
{% endfor %}
---
<div><small><em>
{% assign taglist = "" %}
{% assign prefix = "" %}
{% for tag in tags %}
    <!-- <a href="#{{ tag }}" onclick="myFunction();return false;">{{ tag }}</a>  -->
    {{ prefix }}<a href="#" onclick="myFunction('tag_{{ tag }}');return false;">{{ tag }}</a>
    {% assign prefix = "&nbsp;|&nbsp;" %}
{% endfor %}
</em></small></div>

<p>
  When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
  \[x = {-b \pm \sqrt{b^2-4ac} \over 2a}.\]
</p>