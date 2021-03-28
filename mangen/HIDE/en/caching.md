# Кэширование и ленивые объекты.

Особенностью скриптового cad является необходимость перезапуска скрипта генерации геометрии при каждом обновлении модели. С ростом размера модели это приводит к значительному росту времени, требующегося на расчёт и отрисовку геометрии. С целью решения этой проблемы вычислительно ёмкие операции ZenCad закешированы и ленифицированы силами библиотеки [evalcache](https://github.com/mirmik/evalcache). 

Вместо непосредственного расчета, evalcache строит дерево построения модели на основе хэшключей генерируемых объектов. Библиотека сохраняет в кэше на жестком диске все произведенные вычисления и в случае, если объект уже был расчитан ранее, достаёт его из кэша. evalcache отслеживает изменения параметров в дереве модели и на лету обновляет переставшие быть актуальными объекты вычисления.

### Отладка в условиях работы с ленивыми вычислениями.
Так как evalcache выполняет вычисления только в момент, когда объект в действительности запрошен, а не тогда, когда он объявлен, могут возникать проблемы с пониманием точки возникновения возможной ошибки. Также могут возникать проблемы из-за неявного раскрытия ленивых объектов на некоторых операциях.

Для отладки и понимания точки возникновения ошибки можно применять следующие опции:

```python
zencad.lazy.diag=True # Активировать вывод информации об операциях библиотеки кеширования.
zencad.lazy.fastdo=True # Выполнять запрос объекта в момент его создания.
zencad.lazy.encache=False # Запретить сохранение в кэш.
zencad.lazy.decache=False # Запретить загрузку из кэша.

zencad.lazy.onbool=False # Запретить автоматическое раскрытие на булевых операциях
zencad.lazy.onstr=False # Запретить автоматическое раскрытие при преобразовании к строке.

zencad.lazy.onplace=True # Раскрывать объект в момент его создания (не рекомендуется, может нарушать логику).
```

Дополнительные опции можно найти в документации к коду библиотеки evalcache.

----
### Где лежит кэш?
По умолчанию кеш располагается по локальному адресу `~/.zencadcache`, где _~_ - домашний директорий пользователя.