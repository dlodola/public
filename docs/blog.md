<ul>
  {% for post in site.posts %}
    <li>
      <a href="/public{{ post.url }}">{{ post.title }}</a>
      <div id="test">{{ post.excerpt }}</div>
    </li>
  {% endfor %}
</ul>
