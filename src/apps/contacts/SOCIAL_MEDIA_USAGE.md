# Использование социальных сетей в шаблонах

## Добавленные поля в модель Office

В модель `Office` добавлены следующие поля для социальных сетей:

- `instagram` - URL профиля Instagram
- `facebook` - URL страницы Facebook
- `linkedin` - URL профиля LinkedIn
- `twitter` - URL профиля Twitter/X
- `youtube` - URL канала YouTube
- `telegram` - Username или ссылка на канал Telegram
- `whatsapp` - Номер телефона для WhatsApp
- `tiktok` - URL профиля TikTok

## Методы модели

### `get_social_media()`
Возвращает словарь с активными социальными сетями. Каждая соцсеть содержит:
- `name` - название
- `url` - ссылка
- `icon` - FontAwesome класс иконки

### `has_social_media()`
Проверяет, есть ли хотя бы одна заполненная социальная сеть.

## Примеры использования в шаблонах

### Пример 1: Вывод иконок социальных сетей (горизонтальный список)

```django
{% if office.has_social_media %}
<div class="social-links">
  {% for key, social in office.get_social_media.items %}
  <a href="{{ social.url }}" target="_blank" rel="noopener noreferrer" class="social-link" title="{{ social.name }}">
    <i class="{{ social.icon }}"></i>
  </a>
  {% endfor %}
</div>
{% endif %}
```

**CSS для горизонтального списка:**
```css
.social-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-dark);
  color: white;
  font-size: 1.125rem;
  transition: all 0.3s;
  text-decoration: none;
}

.social-link:hover {
  background: var(--accent-gold);
  color: var(--txt-dark);
  transform: translateY(-3px);
}
```

### Пример 2: Вывод с названиями (вертикальный список)

```django
{% if office.has_social_media %}
<div class="social-list">
  <h4>Мы в социальных сетях</h4>
  <ul>
    {% for key, social in office.get_social_media.items %}
    <li>
      <a href="{{ social.url }}" target="_blank" rel="noopener noreferrer">
        <i class="{{ social.icon }}"></i>
        <span>{{ social.name }}</span>
      </a>
    </li>
    {% endfor %}
  </ul>
</div>
{% endif %}
```

### Пример 3: Футер с социальными сетями

```django
<!-- В footer -->
<footer class="footer">
  <div class="container">
    <div class="footer__content">
      <!-- ... другое содержимое ... -->

      {% if main_office.has_social_media %}
      <div class="footer__social">
        <h4>Следите за нами</h4>
        <div class="footer__social-links">
          {% for key, social in main_office.get_social_media.items %}
          <a href="{{ social.url }}" target="_blank" rel="noopener noreferrer" aria-label="{{ social.name }}">
            <i class="{{ social.icon }}"></i>
          </a>
          {% endfor %}
        </div>
      </div>
      {% endif %}
    </div>
  </div>
</footer>
```

### Пример 4: Контактная страница

```django
<!-- На странице контактов -->
<div class="office-card">
  <h3>{{ office.city }}</h3>
  <p>{{ office.address }}</p>
  <p>
    <i class="fas fa-phone"></i> {{ office.phone }}
  </p>
  {% if office.email %}
  <p>
    <i class="fas fa-envelope"></i> {{ office.email }}
  </p>
  {% endif %}

  {% if office.has_social_media %}
  <div class="office-social">
    {% for key, social in office.get_social_media.items %}
    <a href="{{ social.url }}" target="_blank" rel="noopener noreferrer" class="social-icon">
      <i class="{{ social.icon }}"></i>
    </a>
    {% endfor %}
  </div>
  {% endif %}
</div>
```

### Пример 5: Отдельные проверки для каждой соцсети

Если нужно отобразить определенные соцсети в определенном порядке:

```django
<div class="social-links-custom">
  {% if office.instagram %}
  <a href="{{ office.instagram }}" target="_blank" rel="noopener noreferrer" class="social-instagram">
    <i class="fab fa-instagram"></i>
  </a>
  {% endif %}

  {% if office.facebook %}
  <a href="{{ office.facebook }}" target="_blank" rel="noopener noreferrer" class="social-facebook">
    <i class="fab fa-facebook-f"></i>
  </a>
  {% endif %}

  {% if office.whatsapp %}
  <a href="https://wa.me/{{ office.whatsapp|cut:'+' |cut:' '|cut:'-' }}" target="_blank" rel="noopener noreferrer" class="social-whatsapp">
    <i class="fab fa-whatsapp"></i>
  </a>
  {% endif %}
</div>
```

## Заполнение в админке

1. Перейдите в Django Admin → Офисы
2. Выберите офис для редактирования
3. Раскройте секцию "Социальные сети"
4. Заполните нужные поля:
   - **Instagram, Facebook, LinkedIn, Twitter, YouTube, TikTok**: Вставьте полную ссылку (например: https://instagram.com/username)
   - **Telegram**: Можно указать username (@username или просто username) или полную ссылку
   - **WhatsApp**: Укажите номер телефона в международном формате (например: +77172123456)

## Примечания

- Все поля необязательные - заполняйте только те, которые используются
- Ссылки автоматически откроются в новой вкладке (`target="_blank"`)
- WhatsApp автоматически преобразуется в формат wa.me/номер
- Telegram username автоматически преобразуется в ссылку t.me/username
- Используются FontAwesome иконки (они уже подключены в проекте)
