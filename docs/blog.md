<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{site.url}}/{{ post.url }}">{{ post.title }}</a>
      <div class="test">{{ post.excerpt }}</div>
    </li>
  {% endfor %}
</ul>
