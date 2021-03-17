<ul>
  {% for post in site.posts %}
    <li>
      <a href="/public{{ post.url }}">{{ post.title }}</a>
      {{ post.excerpt }}
    </li>
  {% endfor %}
</ul>
