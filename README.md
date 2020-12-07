# Kivyx : An experiment of Kivy widgets

## Dependencies

```
pip install git+https://github.com/gottadiveintopython/asynckivy.git@master#egg=asynckivy
```

## LICENSE

Everything in the repository can be used under MIT license except the stuffs inside `assets_just_for_tests_and_examples` directory. They are not mine.

## TODO(api break)

- rename `KXMagnet2` to `KXMagnet`, and remove the original `KXMagnet`.
- remove `kivyx.utils.fade_transition` since `asynckivy` already has it.

## TODO

- flagを用いてtouchを二重に処理してしまわないようにする
- KXDrawerの実装から`ak.or_()`を除く
