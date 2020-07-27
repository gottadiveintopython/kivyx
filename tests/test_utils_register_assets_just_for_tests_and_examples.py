def test():
    from kivy.resources import resource_find
    from kivyx.utils import register_assets_just_for_tests_and_examples
    register_assets_just_for_tests_and_examples()
    assert resource_find(r'nothing_other_than_test')
